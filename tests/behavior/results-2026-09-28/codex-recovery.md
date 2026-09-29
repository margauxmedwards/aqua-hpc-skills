**ram:** Cell 2 failed from confirmed host RAM exhaustion at 8 GB. A retry at 12 GB is justified by the 10 GB live-set estimate and fits the authorized 16 GB cap. I could resubmit only cell 2, preserving its configuration and verified original resource settings within the 2-hour cap. Cells 0 and 1 remain validated. No submission was performed or evidenced.

**walltime:** Cell 4 exhausted its 2-hour limit. The checkpoint’s configuration hash differs, so I could not safely resume it. A full restart requesting 3 hours, including margin, fits the authorized one-retry, 4-hour ceiling. No submission was performed or evidenced.

**cap:** No further retry is authorized: the sole retry is exhausted, and both the user cap and eligible queue limit are 4 hours. The estimated 6-hour run cannot fit, and checkpointing is unsupported. Recovery would require a revised budget plus a verified longer eligible route, or an approved change enabling shorter runs. Nothing was resubmitted.
