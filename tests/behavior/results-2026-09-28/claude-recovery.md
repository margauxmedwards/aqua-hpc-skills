**ram:** Cell 2 ran out of host memory. PBS history shows the job has finished, and stderr says it exceeded the 8 GB host-memory limit. I've prepared a replacement for cell 2 only:
- **Memory:** 8 GB → 12 GB. The estimated peak memory in use is 10 GB, and 12 GB is within your 16 GB cap.
- **Everything else:** RPID, configuration, data and code stay the same. This is attempt 1 of 1, and there is no earlier retry or replacement already running.
- **Walltime and CPUs:** I haven't confirmed these match the original request yet. I only know the 2h cap, not what the original job asked for, so I'll check the original request before submitting.
- **Cells 0 and 1:** already validated and left as they are.

**Not submitted yet:** I have no qsub result, so there's no new job ID. Once it's submitted, I'll report the ID and link it to the original cell 2 job.

**walltime:** Cell 4 hit its 2h walltime while still making steady progress. I can't continue where it left off: the existing checkpoint was made with a different configuration from this cell, so resuming from it isn't safe. The fix is to rerun cell 4 from the start, with the same configuration:
- **Walltime:** 02:00:00 → 03:00:00. That's the estimated full runtime including margin, and it's within your 4h cap.
- **Retry:** this uses your one allowed retry. No replacement is running.
- **Tradeoff:** the progress from the first run is lost and the old checkpoint won't be used. The old outputs will be kept.

**Not submitted yet:** it's prepared, but I have no qsub result or new job ID.

**cap:** I haven't requeued it because this is blocked on your decision. The job has finished and already used the only retry you allowed, at 4h. It needs about 6h, but both your cap and the maximum walltime on the eligible queue are 4h. It also can't resume from a checkpoint, so running it again at 4h would just hit the limit again.

Options that need your decision:
1. **More budget:** raise the retry and walltime limits to at least 6h, and I'll check whether there's an eligible queue that allows jobs longer than 4h.
2. **Checkpointing:** add checkpoint and resume support, test it on a small case, then run it in chunks of under 4h.
3. **Splitting:** break the work into smaller cells that each finish within 4h. This only works if splitting doesn't change the scientific meaning of the results.

Nothing has been submitted, and the outputs from the failed run are kept.
