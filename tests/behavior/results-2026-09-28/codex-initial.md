submit: Using the supplied Aqua HPC skill: the locked environment and smoke-output validation passed. The authorized scope is 8 cells, at most 2 concurrent. Submission remains pending; no qsub result or job ID is evidenced.

queue: Recommend general GPU placement: it supports the validated H100 hardware and required 60h within its 72h limit. QCR’s A100 hardware and 48h limit do not meet these requirements. Use `gpu_batch` with a verified H100/general placement selector; direct submission to `qcr-users` is prohibited by its route-only restriction. Queue wait is unknown.

waittime: Request **01:15:00 walltime**: 5 minutes startup + 50 minutes processing + 5 minutes finalization, with 25% headroom. This fits the 2h queue limit. Queue wait is unknown.

progress: As of **28 September 2026, 14:00 AEST**, 8 cells total: **3 validated, 1 running, 1 queued, 2 failed, 1 unsubmitted**. Cell 3 has fresh progress of 50/100. Cell 6 exited zero but failed validation with 0/100 outputs. ETA unknown; no retry was performed.

repair: Cell 5 failed because it used `/usr/bin/python` instead of the prepared Pixi environment; the dependency already exists in `pixi.lock`. The correct activation import preflight passed. I could correct the launcher in a new recorded revision and retry cell 5 once within budget, preserving cell 6’s live code. No edit, end-to-end validation, or resubmission is evidenced.

ram: Cell 2 has confirmed host-RAM exhaustion at 8GB. A 12GB replacement is justified by the 10GB live-set estimate and fits the authorized 16GB ceiling. I could submit its single retry with unchanged configuration and walltime within 2h, preserving validated cells 0–1. No replacement ID is evidenced.

vram: This was GPU VRAM exhaustion; increasing host RAM to 64GB would not address it. Batch size must remain fixed. Recovery requires a decision authorizing verified larger-VRAM hardware or a scientifically meaningful configuration change. No retry occurred.

walltime: Cell 4 exhausted its 2h limit, but the checkpoint’s mismatched configuration makes it unsuitable for resuming. A full restart estimated at 3h fits the authorized single retry and 4h ceiling. I could submit that replacement while preserving the incompatible checkpoint; no resubmission is evidenced.

unknown: Submission status is unknown: the transport timeout may have occurred after PBS accepted the job, and the scheduler query also failed. Reconcile the original submission before retrying to avoid a duplicate. The stale RUNNING marker does not establish current state; no retry occurred.

storage: The failure is exhausted inode quota, despite available disk bytes. More RAM would not help. Recovery requires an authorized scoped cleanup or approved alternate storage before rerunning. Neither storage changes nor resubmission occurred.

health: At **14:10 AEST**, one Aqua login host was reachable, but `qstat -B` timed out. PBS health is unresolved; queue/node state is unknown and compute execution was not tested. This does not establish either full service health or a cluster-wide outage.

poll: Existing service **campaign-monitor-1** polls cells 0–7 every 10 minutes until **15:00 AEST**, writing local `status.json`. Its last supplied snapshot, **14:00 AEST**, reports 3 validated, 2 running, 1 queued, 1 failed, and 1 missing. No fresh snapshot was obtained; the monitor has no chat/push delivery channel.

stop: The identified target is **campaign-monitor-1** only. I could stop that monitor while leaving PBS jobs **456 and 457** and the shared SSH/SSHFS connection running. No monitor-stop result is evidenced.

cap: Recovery is blocked: the sole authorized retry is exhausted, and both the user ceiling and queue limit are 4h. The estimated 6h workload cannot fit without checkpointing. Another attempt requires a revised recovery budget and an eligible longer route or validated splitting/checkpoint strategy. No resubmission occurred.
