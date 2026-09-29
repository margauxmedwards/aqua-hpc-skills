# RPID and PBS on Aqua

## RPID in three steps

1. Sign in to the [QUT Data Management Plan system](https://data-mgmt-plan.qut.edu.au/) and locate the relevant research project's RPID. Ask the project lead or eResearch if you cannot find it or need access. Exact menu labels have not been verified; do not invent them.
2. Add `#PBS -P ABCDEF1234` alongside the other directives at the top of the script, replacing the example with your authorized RPID (six uppercase letters and four digits).
3. Submit normally, or supply it explicitly: `qsub -P "$AQUA_RPID" job.pbs`. Use the same accounting flag for arrays and interactive jobs.

The notice supplied on 28 September 2026 says RPID inclusion becomes mandatory on **2 November 2026**. Aqua's live scheduler notice confirmed the syntax and format on 28 September. A no-RPID smoke job ran during the transition, but that does not validate RPID authorization. A format check cannot establish project membership. See [sources](sources.md) for verification limits and official links.

PBS directives are parsed before the shell runs: `#PBS -P $AQUA_RPID` does **not** expand a shell variable. Use a literal identifier or the quoted command-line flag. Put all directives before executable statements.

## Minimal CPU test

```bash
#!/bin/bash
#PBS -N smoke
#PBS -q cpu_batch
#PBS -l select=1:ncpus=1:mem=1gb
#PBS -l walltime=00:02:00
#PBS -j oe
# RPID supplied by qsub -P
set -euo pipefail
cd "${PBS_O_WORKDIR:?}"
printf 'job=%s host=%s\n' "$PBS_JOBID" "$(hostname)"
awk 'BEGIN {for(i=1;i<=100000;i++)s+=i; if(s!=5000050000)exit 1; print "CPU PASS"}'
```

Use `qstat -Q` to inspect available queues. Public routing queues observed in September were `cpu_batch`, `gpu_batch`, `cpu_inter`, and `gpu_inter`; verify current availability. Do not copy lab-only queue names into a general recipe. Resource labels, GPU models, limits and membership are site-specific.

```bash
qsub -P "$AQUA_RPID" smoke.pbs
qsub -P "$AQUA_RPID" -J '0-7%2' array.pbs
qsub -P "$AQUA_RPID" -I -q cpu_inter -l select=1:ncpus=1:mem=2gb -l walltime=00:10:00
qstat -u "$USER"
qstat -f 'JOB_ID'
qstat -xf 'JOB_ID'  # history, if retained by the server
```

Quote array IDs containing brackets. `PBS_ARRAY_INDEX` selects a manifest row; array children need distinct outputs. Validate current array/concurrency syntax with `qsub --help` or the site's manual before adapting templates.

Size resources from a measured smoke run and peak live data, with headroom. CPU workers and BLAS threads must fit the CPU allocation. Low GPU utilization does not prove a GPU is unnecessary. Free GPUs may belong to another queue: placement, walltime, architecture and access constraints matter more than a cluster-wide free count.

Create scheduler output directories before submission; do not put `$PBS_JOBID` in output directives expecting runtime expansion. `cd "$PBS_O_WORKDIR"` before relative paths, and include the array index and an attempt identity in run paths.
