# Bounded resource recovery

A request to fix/requeue failed experiments permits the stated recovery; retain previous authorization rather than asking again for every cell. Record maximum attempts per cell, maximum memory/walltime/GPU class, concurrency, and campaign resource budget. If these already exist, use them. Without established caps, diagnose and prepare a concrete proposal, then ask for the missing resource ceiling before increasing allocations. Do not silently choose unlimited doubling. A useful user policy is “at most one retry per failed cell, up to 32 GB and four hours, at most two concurrent, preserving the scientific configuration.” This is an example, not a global default.

A resource ceiling is not the original request or the new chosen request. Read the original PBS request before saying “same walltime/CPU/GPU”; when only a cap is known, say the unchanged request still needs verification. Preserve known original settings and choose the minimum justified changed resource within caps. Do not silently set every resource to its maximum.

## Diagnose the exhausted resource

| Evidence | Likely cause | Appropriate response |
| --- | --- | --- |
| Explicit PBS/cgroup memory-limit kill with host-memory telemetry | Host RAM exhaustion | Estimate peak live memory and retry with justified RAM headroom within caps; preserve CPUs/GPU placement unless also diagnosed |
| Framework `CUDA out of memory` and VRAM telemetry | Device memory exhaustion | More PBS `mem` does not add VRAM; investigate model/batch footprint or a verified larger-VRAM GPU |
| PBS walltime termination near requested limit with continuing progress | Runtime limit exhausted | Estimate remaining/full runtime, check limits, and resume a verified checkpoint or restart with enough total time |
| `No space left on device`, quota/inode errors | Storage exhaustion | Check filesystem bytes, inodes and quota; move/stage to approved storage or propose scoped cleanup; RAM/walltime changes do not solve this |
| Generic killed process, exit 137/nonzero, absent logs | Ambiguous | Gather corroborating PBS/stderr/telemetry evidence; do not classify from the exit code alone |
| Long run without output/heartbeat progress | Possible deadlock, bad input, stalled ROS readiness or I/O | Diagnose liveness; extending walltime can just extend a stall |

Recorded memory peaks can under-report a sudden allocation that caused a kill. Use application peak-live-set estimates as well as observed usage; do not prescribe a lower request than the failed limit just because sampled telemetry was low. `mem` is host memory per select chunk: account for all chunks/nodes when calculating total costs. A GPU model label alone may not identify its VRAM capacity; verify the actual device variant.

Changing batch size, precision, input resolution, model, sensor, sampling or numerical behavior can affect scientific comparability. Use an already authorized equivalent mode or explain the change and seek the needed decision. Preserve these settings when a hardware-only recovery is sufficient. Do not downsample silently to make the job finish.

## Replacement sequence

1. Reconcile PBS history, stderr, timestamps and output/checkpoint records. Prove the original child is terminal and there is no live replacement. `Q`, `R`, `H`, `E`, a submission timeout or unknown status does not authorize a duplicate. A held job can still run later. Do not delete it as a shortcut.
2. Identify failed/missing original manifest indices, not the entire array. Preserve validated cells. Maintain stable scientific cell IDs and write to a new attempt directory.
3. Check the proposed resources against the user caps, current site limits, eligible hardware and remaining campaign budget. Record old/new requests and the evidence. Do not use `qrerun` expecting new resource limits; for terminal jobs prepare a new `qsub -P` submission with explicit resources. Do not claim a running job can have limits extended without verified site support.
4. Resume only a checkpoint validated against code/config/data identity, completeness and application resume semantics. Stage a copy/reference safely, never overwrite the source. Without a compatible checkpoint, budget for a full restart; a longer walltime does not recover prior progress by itself.
5. Validate the repair in a representative small case where appropriate, then submit only the affected cells within concurrency limits. Record the new ID immediately and the old→new mapping. If submission is ambiguous, stop and reconcile; do not blindly repeat it.
6. Verify replacement output against the original completeness contract and scientific configuration. Stop at the retry/resource cap or on repeated deterministic failure. Report unresolved cases and the specific next decision.

For an unchanged production manifest, a retry might select `-J '2,5'` (verify site syntax). Keep those original indices. If writing a new compact retry manifest, explicitly map new indices to original cell IDs. The CPU demo in this repository illustrates output validation but does not implement checkpointing or automatic resource recovery; adapt the production runner instead of claiming these capabilities exist in the demo.
