# Response evaluation — 28 September 2026

Executed fresh noninteractive Codex and Claude Code sessions against all 14 [synthetic scenarios](../scenarios.json), using the skill and its common-request, queue/time and recovery references. The prompt requested a concise response for each independent scenario using only the supplied evidence; the rubric was not included. No live tools, HPC jobs, file edits or monitor changes were requested or executed by the evaluators.

- Codex CLI 0.156.1, configured default model `gpt-6-astra`, ephemeral read-only session.
- Claude Code 2.1.281, configured default model (not independently recorded), no tools and no session persistence.
- Both completed successfully within a 240-second watchdog. Outputs were nonempty, covered every case and were manually assessed against the rubric; this was not a keyword-match test.

## Results and correction

Both initial runs handled the material safety/decision cases: general H100 placement instead of incompatible route-only QCR, 75-minute walltime with unknown queue wait, 3/8 validated progress, unknown-submission reconciliation, VRAM versus host RAM, inode exhaustion, incompatible checkpoints, exhausted budgets, layered health, reuse of an existing poller and stopping only that monitor.

One grounding issue emerged: Claude's initial host-RAM response called the 2h **cap** the “same 2h walltime,” although the original request was not supplied. The skill now explicitly separates original requests, proposed allocations and user ceilings, and requires checking the original request before asserting unchanged resources.

Fresh sessions then repeated the RAM, walltime and exhausted-budget cases. Both kept RAM recovery bounded, treated the existing resource settings as requiring verification, rejected the incompatible checkpoint and declined escalation beyond the exhausted budget. No remaining material deviation was found in that targeted pass. The other 11 cases were not rerun after this narrow clarification.

## Inspect the actual responses

- [Codex: 14 initial cases](codex-initial.md)
- [Claude: 14 initial cases](claude-initial.md)
- [Codex: 3 recovery cases after clarification](codex-recovery.md)
- [Claude: 3 recovery cases after clarification](claude-recovery.md)

These are offline response tests, not proof that an agent executed a repair, stopped a monitor, or submitted a job. The runnable toolkit's eight local tests also passed. A separate read-only Aqua query checked current routing/limits; no QCR/RPID submission or live automatic recovery was tested. Future model behavior and site settings can change.
