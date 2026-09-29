# Monitoring, data and recovery

Batch status/log queries into one SSH call. Reuse a configured SSH connection where permitted and use one bounded watcher per campaign. Do not launch an SSH connection per array cell or a tight polling loop. Choose a minutes-scale interval appropriate to site guidance; this is a recommendation, not a documented QUT rate limit. Check for an existing watcher before starting another and record its PID, scope and stopping condition.

An existing SSHFS mount can serve small progress files without repeated authentication, but caching can make it stale. Confirm material state changes with a bounded direct read and PBS accounting. Avoid recursive scans of huge remote trees or treating the mount as a bulk-transfer channel. A status timeout, empty response or inaccessible scheduler means **unknown**, not finished or recovered.

Use `qstat -f` comments and hold types to distinguish capacity, placement, RPID, environment and scheduler problems. System holds can require an operator; do not repeatedly try to release them or automatically delete jobs. Preserve IDs/logs, confirm original jobs cannot still execute, and only resubmit under the user's authorized scope. If submission times out, reconcile queue/history and recorded run identity before retrying: it may already have been accepted.

Store code, inputs, temporary scratch and durable results according to current quotas and retention policy. Scratch is not a backup. Transfer directories with `rsync -avhP`; inspect trailing-slash semantics and a dry run before a large synchronization. Use checksums/manifests for important inputs; file sizes/counts alone are not integrity checks. Do not use `--delete` or remove scratch output without a scoped cleanup decision. Stage many small files as an archive where suitable and validate extraction.

For experiment tracking, local JSON/CSV plus provenance is sufficient. W&B is optional: preinstall it in the pinned environment, use one offline run per attempt, and sync explicit completed run directories later when authorized. Do not auto-upload all historical runs. Authenticate outside versioned files and avoid printing API keys, full environments, credential files or raw scheduler variable lists.

Failure triage order: PBS state/exit and logs; resolved executable and input paths; effective environment; CPU/memory/walltime/GPU compatibility; data coverage; I/O and middleware. Change one diagnosed cause, run a representative smoke case, then resume the missing work. Preserve failures for analysis.
