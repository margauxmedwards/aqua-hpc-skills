# QCR/general placement and time estimates

## Discover before recommending

Use one bounded remote query for `qstat -Qf` on candidate routing and execution queues, selected node/resource information, and (where authorized) current group membership. Inspect `queue_type`, `from_route_only`, `route_destinations`, `acl_group_enable`, `acl_groups`, `resources_max.*`, enabled/started state and per-user limits. Server/site hooks may add restrictions that queue output alone does not reveal. Existing successful jobs can demonstrate routing, not entitlement for every user.

**Observed on Aqua, 28 September 2026:** `gpu_batch` was a routing queue whose destinations included `gpu_batch_exec` and `qcr-users`. `qcr-users` was an execution queue with `from_route_only=True`, group ACL `qcr-users`, default `qlist=qcr-users`, maximum walltime 48 hours and a per-user GPU running limit of four. These are a dated snapshot, not permanent limits or a promise of access/capacity.

Use the verified public route, e.g. `-q gpu_batch`; a desired QCR placement can require `qlist=qcr-users` **inside the select chunk**, subject to current site guidance/hooks. Do not submit directly to a route-only execution queue. Example syntax to adapt only after entitlement and placement are verified:

```bash
qsub -P "$AQUA_RPID" -q gpu_batch \
  -l select=1:ncpus=4:mem=16gb:ngpus=1:qlist=qcr-users \
  -l walltime=02:00:00 job.pbs
```

## GPU model

GPU nodes advertise a `gpu_id` resource. A read-only `pbsnodes -av` on 28 September 2026 showed mostly `A100` and `H100` nodes, plus a few mixed-model nodes. Choosing a model is an option, not a default: omit `gpu_id` to accept any GPU, or add it inside the select chunk when the workload needs one architecture (for example, compiled kernels validated only on that GPU) or when comparing timings:

```bash
#PBS -l select=1:ncpus=8:mem=32gb:ngpus=1                # any GPU model
#PBS -l select=1:ncpus=8:mem=32gb:ngpus=1:gpu_id=A100    # A100 only
#PBS -l select=1:ncpus=8:mem=32gb:ngpus=1:gpu_id=H100    # H100 only
```

Ask the user or check the project's validated hardware before pinning; never assume one model is required. Pinning narrows eligible nodes and can lengthen queue wait.

Removing the QCR placement constraint leaves routing to the site; it does not necessarily exclude QCR nodes. If an experiment must use the general execution pool, establish the site's supported selector rather than guessing a queue override. Preserve tested GPU architecture requirements; do not add an A100/H100 constraint just because an example uses one. Node state `free` and aggregate GPU counts do not prove enough eligible unallocated resources exist; check assignments and avoid double-counting parent nodes and vnodes.

Prefer the eligible option with the best supported time-to-result for this workload. QCR is not a universal priority boost; it may be a smaller shared pool, and general capacity may be more suitable for large arrays or longer jobs. CPU-only analysis normally starts with `cpu_batch`; GPU inference requires a compatible GPU allocation. Never submit duplicate jobs to both pools to race for a slot.

## Runtime limit versus queue delay

Estimate total runtime as:

`startup + measured work rate × full work size + checkpoint/finalization + margin`

Measure on representative hardware and inputs, exclude warmup from steady-state throughput, and include it once as startup. Use multiple representative cases or a conservative percentile where runtimes vary. If the smoke run already includes startup, do not count it twice when scaling. Account for non-linear costs, I/O, model loading, ROS readiness and checkpoint writes. Example only: 5 minutes startup + 10,000 records at 0.3 seconds/record + 5 minutes finalization = 60 minutes; 25% headroom gives a 75-minute (`01:15:00`) request. The margin is an estimate, not site policy.

Check both queue/server limits and the user's resource cap. A job estimated at 60 hours cannot simply be squeezed into a 48-hour queue: use an eligible longer route or a validated checkpoint/chunk strategy. Larger limits can reduce backfill opportunities, but under-requesting wastes completed work. Shorten an oversized request only from evidence, not to make an unfinishable job start sooner.

Queue delay depends on priorities, eligible resources, reservations and other jobs. If a scheduler start estimate is available, label its observation time and uncertainty. Otherwise state “queue wait unknown.” Queue length or a resource snapshot alone cannot yield a trustworthy ETA.
