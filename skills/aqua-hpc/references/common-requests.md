# Common requests and response formats

Use these formats for Codex, Claude Code and Copilot. Adapt the length to the request; omit empty fields. Bracketed values below are placeholders, not observations. Report only actions actually taken and values supported by evidence. Distinguish observed requests from budget ceilings; a two-hour cap does not prove the original job requested two hours. A request to run or fix work authorizes the necessary scoped actions, subject to existing permissions and budget; do not ask for the same approval again. A status question alone does not authorize cancellation, changed experiments or new submissions.

## “Run this experiment for me on the HPC”

Inspect the entrypoint, flags/config, inputs, environment and output contract. Reuse the supplied SSH alias, RPID and run budget. Prepare a versioned snapshot, run a representative smoke case, validate it, and submit the requested bounded workload. If a necessary value is missing, finish independent preparation and ask only for that value. Do not invent an RPID, expand the matrix, or silently run a scientifically different fallback.

Suggested response after submission:

> Submitted [N cells] as [PBS ID] using [routing queue / placement]. Each requests [CPU, RAM, GPU, walltime], with [N] concurrent. The smoke case passed [specific output check]. Results: [path]. Current state: [queued/running]; full results are not yet validated.

Before submission or when blocked, say “Prepared” and name the missing prerequisite. Never reuse the submitted wording for a dry run or ambiguous qsub response.

## “Which queue should I use—QCR or general?”

Read [queue and time selection](queue-and-time.md). Inspect current queue ACLs, routing, limits and hardware eligibility, then the workload's needs and measured performance. Recommend one route/placement and explain the decisive evidence. QCR affiliation, RPID authorization and scheduler queue membership are different checks.

Suggested format:

| Option | Eligible for this job? | Relevant constraint |
| --- | --- | --- |
| QCR placement | [yes/no/unverified] | [ACL, hardware, size or walltime limit] |
| General CPU/GPU route | [yes/no/unverified] | [compatible capacity and limits] |

> I recommend [option] because [observed evidence]. Use [verified route/placement syntax]. Queue delay is [unknown / scheduler estimate with timestamp]; this is not a guaranteed start time.

Do not offer `qsub -q qcr-users` when the live queue is route-only. Do not confuse a routing queue's zero jobs with an empty execution pool.

## “What waittime should I use?”

Cover both possible meanings without a needless clarification round: **walltime** is the runtime limit requested from PBS; **queue wait** is the delay before starting. If the distinction remains material, ask which they mean while examining prior runs.

> Request [HH:MM:SS] walltime: [startup + workload + finalization estimate], plus [justified margin], within [queue limit]. Evidence: [representative run and input size]. Queue wait is [unknown / dated estimate]. [Checkpoint or split strategy if the estimate exceeds limits].

Use the calculation in [queue and time selection](queue-and-time.md). State uncertainty when a smoke sample misses startup, worst-case inputs or later training phases. Never promise a finish time from queue length alone.

## “How are my experiments going?”

Read one batched scheduler snapshot and small progress/result files, reconcile with the original manifest, and give an observation time. Separate unique cells from attempts and scheduler state from validated outputs. Categories in a totals line must be mutually exclusive and sum to the expected cell count; report an exiting or unverified cell explicitly rather than double-counting it.

> As of [timestamp/timezone], [validated]/[expected] cells are validated. [N] running, [N] queued, [N] failed, [N] held, [N] missing/unsubmitted, [N] awaiting validation, [N] unknown. [Only include applicable categories.]
>
> Running progress: [records/steps/checkpoint and freshness]. Main blocker: [evidence]. ETA: [range and basis, or unknown]. Results: [path].

Use a per-cell table only for exceptions or a small campaign. Label stale mount data and failed scheduler queries; disappearance from qstat is not completion. Do not start a persistent watcher unless monitoring is requested, and record its end condition when it is.

## “Have there been errors? Can you check and fix them?”

Triage logs, PBS records, output coverage and runtime provenance. “Check and fix” permits scoped fixes and a representative validation; retry within the established run/resource budget. Read [recovery](recovery.md) before resubmission. Preserve original failures and validated cells. Code changes require a new recorded revision/attempt; do not mutate the code used by live jobs. If a fix changes scientific meaning, disclose it and obtain the needed decision.

> Found [failure] in [cells/IDs], supported by [log/metric]. Fixed [cause] in [revision/path]. Validation: [what actually passed]. Recovery: [new IDs and old→new mapping / prepared but blocked reason]. [N] previously validated cells remain intact. Remaining issue: [if any].

If no error is found, bound the claim: “No errors in [logs/cells checked]; [N] outputs are still unvalidated.” Do not equate exit zero with valid results.

## “If it runs out of memory/walltime, requeue it with more”

This is authorization for resource recovery within the agreed limits, not infinite retries. Read [recovery](recovery.md): distinguish host RAM, GPU VRAM, disk/quota and walltime. Verify the old job is terminal, preserve its outputs, and submit a replacement for only the affected cells. A new submission usually receives a new ID; say “resubmitted” rather than implying the original ID resumed.

> [Old ID / cell] failed due to [confirmed cause]. Resubmitted as [new ID] with [old → new resource], attempt [x/max]. [Resuming verified checkpoint / restarting because no compatible checkpoint]. Same [RPID, config, data and code identity, or explicit changes]. Remaining recovery budget: [cap].

If unable to act, report the specific blocker: uncertain state, unverified checkpoint, queue limit, exhausted retry budget or a scientifically meaningful configuration change. Do not call a proposal a completed repair.

## “Is the HPC working?” / “Is Aqua down?”

Check the layers independently with bounded calls: SSH/login reachability, PBS responsiveness, whether the relevant queue is enabled/started, and (only if authorized) actual compute execution. A stale mount, login banner or TCP connection alone does not establish scheduler/compute health. Conversely an SSH authentication or local network failure does not establish a cluster-wide outage. An enabled queue can still have unavailable nodes.

> Checked at [time]: login [reachable/failed/unknown]; PBS [responsive/failed/unknown]; [queue] [enabled/started/unknown]. Compute execution [verified by job ID + validated output / not tested]. [Observed failure and next diagnostic, if any].

A health question alone permits read-only diagnostics, not spending an allocation on a new job. If the user says “schedule a test,” use a tiny bounded smoke job with their RPID. Report “queued” until actual execution and output validation pass. After a transient failure, require positive valid responses before saying service recovered. Keep host-specific and cluster-wide conclusions separate.

## “Can you poll my experiments?” / “Update?” / “How's it going?”

“Update?” and “how's it going?” normally mean one fresh status snapshot, not starting another background process. Reuse the status format above and the recorded campaign scope. An explicit request to poll permits repeated read-only monitoring for those jobs; inspect existing watchers first and reuse one if possible.

Set and state an interval and finite stop condition. Unless the user supplied them, a reasonable initial session is one check every 10 minutes for up to an hour or until all tracked attempts are terminal; adjust to site guidance and the campaign. This is a local default, not a QUT rule. Do not claim asynchronous updates or notifications unless a monitor and its delivery mechanism actually exist. If the client cannot continue monitoring after the turn, explain the limitation and provide a concrete bounded command/script or monitor setup, without pretending it is running.

A watcher needs one owner, recorded PID/service identity, explicit tracked IDs/manifest, a deadline, bounded connection/command timeouts, and backoff on errors. Prefer batched scheduler reads and compact status files; reuse configured SSH transport. Never spin on a failed command or spawn a new watcher for every “update.” A request to stop polling stops only that identified monitor, not experiments or shared SSH/SSHFS connections.

> Monitoring [campaign/IDs] every [interval] until [deadline or terminal condition]. Monitor: [actual PID/service or active session]. Latest: [validated/expected and current states]. Updates: [actual delivery channel]. [If monitoring could not start, state that instead.]

After repeated transport/scheduler failures, report monitoring as degraded/unknown and stop or back off within the deadline. A poller does not infer recovery, resubmit work, release holds or enlarge resources unless that separate behavior was authorized. At terminal state, validate outputs before declaring the campaign complete; the monitor can finish with failures or incomplete outputs.

## “Where are the outputs?” / “Stop or cancel that”

For outputs, return the run directory, manifest, logs, validated results and provenance; distinguish partial files from final artifacts. Do not automatically upload them externally.

Resolve “that” against recorded job/monitor IDs. Stop a specifically identified monitor without canceling jobs. Cancel only the user's clearly scoped jobs when cancellation is requested; clarify ambiguous scope before `qdel`. Preserve outputs. A stopped watcher and a canceled PBS job are different outcomes and should be reported separately.
