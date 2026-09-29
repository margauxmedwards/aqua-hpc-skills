---
name: aqua-hpc
description: Prepare, submit, monitor, and diagnose QUT Aqua PBS jobs, including RPID accounting, reproducible Pixi environments, ROS workloads, and parameter sweeps.
---
# Aqua HPC

Use for Aqua remote compute and experiment orchestration. Inspect the project's existing runner, flags, configuration, and environment before adapting it. Keep examples independent of any particular sensor, model, dataset, or lab allocation.

## Workflow

1. Establish the SSH alias, remote workspace, approved project RPID, input locations, resource budget, and intended actions. Reuse answers and authorization already supplied. Preparation does not imply permission to start an unbounded campaign.
2. Distinguish local preparation, lightweight login-node administration, and scheduled compute. Discover `qsub`, queues, storage and access; never run workloads or large builds on login nodes.
3. Read [RPID and PBS](references/pbs.md) for submission. Require a real project RPID; never use a fabricated identifier or the temporary no-RPID grace period as a workflow.
4. Stage a versioned snapshot into a new run directory. Record exact revision, lockfile hash, flags and data identity. Inspect remote changes before synchronizing; preserve fixes made on Aqua.
5. Read [environments](references/environments.md) when using Pixi, Python or GPU code, [experiments](references/experiments.md) for arrays/flags, and [ROS](references/ros.md) for robotics. Preflight the actual executable and environment on a representative compute node, then run one small real case before scaling.
6. Record submission IDs immediately. Submission accepted, queued, running, exited zero, and scientifically complete are different outcomes. Validate expected output coverage and content before reporting success.
7. Read [operations](references/operations.md) for monitoring, recovery and transfer. Batch SSH queries, avoid duplicate watchers, and stop bounded retries when evidence requires user or operator input.

For common user requests and concise response templates, read [common requests](references/common-requests.md). For QCR versus general placement or walltime estimates, read [queue and time selection](references/queue-and-time.md). For error repair or memory/time-limit retries, read [bounded recovery](references/recovery.md).

## Reporting

State what was changed or submitted, job IDs, observed state, output locations, validation evidence and unresolved limitations. Log only allowlisted environment metadata, never a full environment or credentials. Do not infer successful execution from empty output, missing queue entries, a progress marker alone, or a successful SSH connection.

Official QUT policy takes precedence over historical operational observations. The maintained source/date notes are in [sources](references/sources.md). Skills do not grant cluster access or override tool permissions.
