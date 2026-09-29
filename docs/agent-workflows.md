# Working with Codex and Claude Code

Both agents consume the same `aqua-hpc` skill, so the operational rules do not depend on a vendor-specific command. Codex supports an explicit `$aqua-hpc` mention; Claude Code exposes `/aqua-hpc`. Natural-language selection also depends on the client's skill discovery and settings. [Codex documentation](https://developers.openai.com/codex/skills); [Claude documentation](https://code.claude.com/docs/en/skills).

See the [common-request cookbook](../skills/aqua-hpc/references/common-requests.md) for response formats covering health checks, one-off updates, bounded polling, submission, queue choice and recovery. “Update?” refreshes status; it does not create another watcher.

For general getting-started tips that apply to both agents, see the [AI4Coding guide](https://margauxmedwards.github.io/ai4coding/) and its [repository](https://github.com/margauxmedwards/ai4coding).

## Typical requests

- **Start a project:** “Inspect this repo's CLI and environment. Prepare a short Aqua smoke job using my supplied RPID and remote directory. Show the command and resource budget; do not submit yet.”
- **Run a bounded campaign:** “The smoke case passed. Submit these 12 manifest rows, maximum two concurrent jobs, with the tested resource request. Save IDs and validate each expected output.”
- **Adapt ROS:** “Run these bags headlessly using the existing launch file, varying sensor configuration and model. Verify overlay paths, effective ROS domain, readiness and message coverage before scaling.”
- **Recover:** “Inspect these PBS IDs and failed logs. Preserve completed outputs, identify terminal missing cells, and prepare at most one replacement attempt per cell.”
- **Summarize:** “Compare validated results against the original manifest. Report missing/failed cells explicitly and preserve run provenance.”

Use the project's existing environment and flags. Give the agent a finite scope rather than “keep trying until everything works.” Separate preview/preparation from authorized submissions, cancellation, cleanup and external metric uploads. Existing authorization should persist; avoid repeated approval questions for routine work already requested.

If switching agents, hand over a small versioned campaign record: immutable run path, code/lock/data hashes, resolved config, manifest, PBS IDs, last known state, validated outputs and remaining work. Do not paste secrets or entire shell histories. One agent owns submissions and retries at a time to prevent duplicate jobs. If parallel agents are explicitly requested, give them independent worktrees and outputs and designate one submitter/monitor.

The local source material included improved shared HPC skills and Claude command/memory guidance. This release carries their general lessons, not personal commands, paper-specific thresholds, private queues or blanket claims that one hardware model is always required.
