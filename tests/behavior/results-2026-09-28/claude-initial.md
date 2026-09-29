**submit**: Prepared, but not submitted yet. Scope is authorized for 8 manifest cells, at most 2 running at once. The locked environment and the representative smoke-output check both passed. No `qsub` call or result exists, so there's no PBS ID and nothing is queued. The next step is to submit those 8 cells, capped at 2 concurrent, using the recorded SSH alias, remote paths and RPID. I'll only report "submitted" once I have a job ID back.

**queue**: Use the general GPU route, not QCR placement.

| Option | Eligible for this job? | Relevant constraint |
| --- | --- | --- |
| QCR placement | No | Only A100 is available, but the workload is validated only on H100. Its 48 h max is below the 60 h the job needs, and there's no checkpointing. |
| General GPU route | Yes | Supports H100 and up to 72 h. |

Your QCR group membership is verified, but that doesn't make QCR usable for this job. Submit through `gpu_batch`, not directly to `qcr-users`, which only accepts jobs from the router. Just dropping `qlist=qcr-users` doesn't guarantee a non-QCR node. Confirm the site's supported selector for the general H100 pool first, and keep the H100 requirement. Request 60 h plus a justified margin, staying within 72 h. Both routes are enabled, but queue wait is unknown because there's no start-time estimate.

**waittime**: This covers both meanings of "waittime":
- **Walltime (runtime limit):** request `01:15:00`. The estimate is 5 min startup + 10,000 × 0.3 s (50 min) + 5 min finalization = 60 min, plus 25% headroom from your representative measurements. That fits within the 2 h queue limit.
- **Queue wait (delay before starting):** unknown, because the scheduler gave no start estimate.

**progress**: As of 2026-09-28 14:00 +10:00, 3/8 cells are validated (cells 0–2). This is the recorded snapshot; I haven't refreshed it.

| State | Count | Cells |
| --- | --- | --- |
| Validated | 3 | 0–2 |
| Running | 1 | 3, with fresh progress at 50/100 |
| Queued | 1 | 4 |
| Failed during run | 1 | 5 |
| Exited 0 but failed validation | 1 | 6 (0/100 outputs) |
| Not submitted | 1 | 7 |

- **Main issues:** cell 5 failed, and cell 6 exited zero but produced nothing, so it is not complete.
- **Retries:** none requested, so none were done.
- **ETA:** unknown for the campaign as a whole.

**repair**:
- **What I found:** cell 5 failed with `ModuleNotFoundError` because it ran under `/usr/bin/python` instead of the prepared Pixi Python. The package is already in the committed `pixi.lock`, so the problem is how the environment is activated, not a missing dependency. An import check using the correct activation passed.
- **Fix:** change the job's launch to use the Pixi environment and record it as a new revision.
- **Recovery plan:** run a representative validation, then make the single corrected attempt for cell 5 with the same resources and scientific config. Cell 6 is still running on the original staged code, so I'll leave it and its code untouched.
- **Done so far:** only the diagnosis. The fix hasn't been edited in, validated or resubmitted, and there's no new job ID.

**ram**: Cell 2 hit its 8 GB host-memory limit; PBS history and stderr both confirm the job is terminal.
- **Retry:** only cell 2, as attempt 1 of 1, at 12 GB (10 GB estimated live set plus headroom). That's within your 16 GB cap, with the same 2 h walltime, config, code, data and RPID.
- **Cells 0–1:** validated, and they stay as they are.
- **Status:** resubmission is ready, but there's no `qsub` result, so no new ID exists yet.

**vram**: I haven't requeued it, because more RAM won't fix this.
- **Cause:** it's a torch `CUDA out of memory` error, meaning the GPU's own memory (VRAM) ran out. Host RAM peaked at 6 GB of the 16 GB requested, and PBS `mem` doesn't add VRAM.
- **Blocked options:** your protocol fixes the batch size, and a different GPU class isn't authorized.
- **What I need from you:** either approve a verified larger-VRAM GPU (checking the actual device's memory, not just its model name), or approve a protocol change. I can also look at the job's VRAM footprint without changing the science.

**walltime**: I can't continue where it left off. The existing checkpoint's config hash doesn't match cell 4, so resuming from it isn't valid.
- **Plan:** a full restart of cell 4 as the single authorized retry, with `03:00:00` walltime. That's the 3 h estimate, which already includes margin, and it's within your 4 h cap. The job is terminal and has no live replacement.
- **Status:** not yet resubmitted, because there's no `qsub` result and no new ID.

**unknown**: I haven't retried it, and shouldn't yet. The earlier `qsub` may have gone through even though no ID was saved. The scheduler query also timed out, and the progress file saying "RUNNING" is stale. Nothing shows the job has finished, so a retry could create a duplicate. Once PBS responds, I need to check your recent jobs and job history, plus the log and output directories, to see whether that submission exists. Only if the job turns out to be terminal and has no replacement will I retry, up to 4 h.

**storage**: I haven't rerun it, because more memory won't help. Host RAM stayed below its limit. The cause is an exhausted inode quota: too many files, even though free space remains. To proceed, choose one:
- approve a scoped cleanup of specific files, which I'd list first;
- approve an alternate storage location;
- approve a change that writes fewer files, if that doesn't alter the results.

**health**: Checked at 14:10 AEST:
- **Login:** reachable on one Aqua login host.
- **PBS:** unknown; `qstat -B` timed out.
- **Queues and nodes:** unknown.
- **Compute:** not tested, and no job was run.

This doesn't show a cluster-wide outage, and it doesn't show Aqua is healthy either. Next I'd retry a time-limited `qstat -B`, try another login host, and check QUT service status. If you want compute tested, I can schedule a tiny smoke job under your RPID.

**poll**: Monitoring is already covered, so I haven't started a second monitor. `campaign-monitor-1` checks cells 0–7 every 10 min until 15:00 AEST and writes a local `status.json`. It can't send chat or push notifications, so check that file or ask me for a snapshot. The last snapshot, from 14:00 and not refreshed, showed 3 validated, 2 running, 1 queued, 1 failed and 1 missing (8 total). If you want monitoring past 15:00, I can extend its deadline.

**stop**: I'll stop only the monitor `campaign-monitor-1`. PBS jobs 456 and 457 keep running, and the shared SSH ControlMaster that also serves SSHFS stays open. The monitor isn't confirmed stopped yet, since I have no stop result.

**cap**: I haven't requeued it, because the recovery budget is used up. The one authorized retry already ran at 4 h. The job needs about 6 h, which is more than both your 4 h cap and the eligible queue's 4 h maximum, and it can't checkpoint. To go further, I need you to either:
- approve a larger budget and a verified longer eligible route, or
- approve adding and validating checkpointing, as a new revision, so the job can run in chunks under 4 h.
