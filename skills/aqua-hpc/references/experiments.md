# Flags, matrices and complete experiments

Keep the scientific command independent of PBS. Expose explicit flags such as `--sensor`, `--model`, `--dataset`, `--seed`, `--config`, `--output`, and bounded smoke inputs. Inspect the existing CLI rather than assuming these names exist. ROS launch arguments may use `name:=value`; adapt at the runner boundary.

Materialize a matrix before submission: one row per valid combination, with a stable ID and an argument list. Validate incompatible sensor/model combinations early. Save the expanded configuration (including defaults), manifest hash, code revision, environment lock hash, input identity, scheduler ID and attempt number. Avoid `eval` or shell strings for user-provided flags; pass an argv list.

Separate preprocessing from repeated evaluation. Cache features or converted bags only when code, input and relevant parameters match; include these in cache keys. Reusing artifacts from a different sensor or checkpoint silently corrupts comparisons.

Use one array per similar resource class. CPU aggregation, GPU inference, bag conversion and native builds can have different requests. Throttle concurrency to protect filesystem and allocation capacity. Submission is not a reason to expand to every possible combination.

Stage immutable code/config snapshots before queueing. Do not rsync a changing shared checkout while another agent switches branches. If a queued job reads a mutable runner or manifest, later edits can change its experiment. Use a detached worktree/archive or a versioned release directory. Preserve and reconcile remote edits before replacing files.

## Completion contract

Exit zero is necessary but insufficient. Define expected record counts or keys, allowed skipped records, required metrics, finite values, sensor coverage and checkpoint/config identity. A zero-row result or a stalled ROS pipeline must fail, even if a wrapper otherwise exits zero.

Write results through a temporary file followed by a same-filesystem atomic rename. Emit a completion record only after validation. Keep expected, submitted, running, failed, missing and validated counts separate. Aggregate against the original manifest; do not let missing rows disappear from the denominator. Distinguish process completion from scientific validity.

For retries, first prove the previous attempt is terminal and inspect existing artifacts. Rerun only failed/missing rows with the same stable cell IDs and a new attempt path. Bound retry count and total resources; repeated deterministic failures require a fix, not another submission. Track the original and replacement PBS IDs. Do not delete or overwrite successful cells.

The repository's `examples/matrix` is a small CPU-only demonstration of argument forwarding, manifest indexing and output validation, not a robotics benchmark. Apply the same structure to ROS bag playback, simulators, training, preprocessing, or model/sensor comparisons.
