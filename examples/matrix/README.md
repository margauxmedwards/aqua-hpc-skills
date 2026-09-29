# A small flag-driven PBS array

This example computes eight tiny deterministic CPU results. Sensor/model labels demonstrate configuration plumbing; they do not load real sensors or models. Requires Python 3.9+ and Bash. No network, extra packages or private inputs are needed inside the job.

## Run locally first

From the repository root, choose a fresh output directory:

```bash
for index in 0 1 2 3 4 5 6 7; do
  python3 examples/matrix/run_cell.py --manifest examples/matrix/matrix.json \
    --index "$index" --output runs/local-demo
done
python3 examples/matrix/check_results.py --manifest examples/matrix/matrix.json \
  --output runs/local-demo
```

The checker requires all eight cells, valid matching configuration, a finite metric, and completion/provenance records. It exits nonzero for missing or changed results. Reusing an existing cell directory is an error, so choose a new directory for another attempt.

## Submit on Aqua

Clone/stage this repository on Aqua. Run the following **on its login node** from the repo root; only lightweight preparation/submission runs there:

```bash
export AQUA_RPID=YOUR_REAL_RPID
# Preview: creates a unique snapshot and prints qsub; does not submit.
python3 scripts/submit_demo.py --run-dir "$HOME/aqua-demo-preview"
# Actual submission: use a separate new directory.
python3 scripts/submit_demo.py --run-dir "$HOME/aqua-demo-run1" --submit
```

Each child requests one CPU, 1 GB and two minutes, with at most two running concurrently. Confirm the routing queue and array syntax are supported by current Aqua policy. The RPID validator checks format, not authorization. The tool rejects the documentation's placeholder ID. It records the exact qsub argv, staged file hashes and PBS ID in `submission.json` and never polls or retries automatically. Treat timeouts/ambiguous responses as unknown and reconcile PBS before resubmitting.

A preview's printed qsub command can also be run manually, but its `submission.json` remains `prepared`; record the returned ID yourself. A fresh `--submit` invocation handles that recording automatically. Keep staged files unchanged after submission.

Check occasionally using the recorded ID, then validate the artifacts:

```bash
qstat -xf 'JOB_ID_FROM_SUBMISSION'
python3 "$HOME/aqua-demo-run1/check_results.py" \
  --manifest "$HOME/aqua-demo-run1/matrix.json" --output "$HOME/aqua-demo-run1/results"
```

The live scheduler is needed to establish terminal job state; the checker establishes artifact completeness. PBS logs are under `logs/`, and each cell has stdout, stderr, provenance, result and validated completion records under `results/`.

For real experiments, replace the demonstrator's CLI/schema and validation contract together. Add data/checkpoint identity and domain-specific coverage, provision the locked environment before scaling, and use the proper GPU/CPU resource class. The [experiment guide](../../skills/aqua-hpc/references/experiments.md) explains stable identities, retries and preprocessing reuse. This demo deliberately does not automate retries or ROS domain allocation.
