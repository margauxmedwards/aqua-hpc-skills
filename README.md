# QUT Aqua agent skills

A community toolkit for QCR researchers running reproducible jobs on QUT Aqua with **Codex, Claude Code, or GitHub Copilot**. Covers ordinary Python/native applications, ROS bag processing and simulation, GPU workloads, and sensor/model/parameter sweeps. Not an official QUT service.

## HTML guides

The [field guide home page](docs/index.html) links to separate pages: [your first job](docs/first-job.html) (a hands-on walkthrough), the [AI agent guide](docs/agents.html) (how the `aqua-hpc` skill works, install, prompt cookbook, maintenance), [RPID](docs/rpid.html) (the 2 November 2026 requirement, script updates and a command builder), the [walltime calculator](docs/walltime.html), [mounting Aqua](docs/mount.html) (SSHFS on Linux/macOS/Windows, SSH connection sharing, polling status files instead of repeated logins), [ROS on Aqua](docs/ros.html) and [notifications](docs/notify.html) (phone alerts for job state changes with [hpc-watch-ntfy](https://github.com/margauxmedwards/hpc-watch-ntfy) and ntfy). [QUT's official Aqua documentation](https://docs.eres.qut.edu.au/about-aqua) takes precedence. All pages work offline, with local-only helpers and no external dependencies. To serve them, run `python3 -m http.server 8000 --bind 127.0.0.1` from this repository and open `http://127.0.0.1:8000/docs/`. Relative reference links need the repository alongside the page.

### GitHub Pages deployment

The Pages workflow builds the guide at the site root and renders the selected Markdown references with Jekyll. It stages only reviewed documentation, runs tests and checks generated links before publishing. Pushes to `main` deploy automatically; manual dispatch is also restricted to `main`. In Settings → Pages, select **GitHub Actions** as the source (already configured for this repository).

The deployed guide is at [margauxmedwards.github.io/aqua-hpc-skills](https://margauxmedwards.github.io/aqua-hpc-skills/).

## RPID: the short version

From **2 November 2026**, the supplied QUT notice says every submitted job must include a research project ID. Find your project's RPID in the [QUT DMP system](https://data-mgmt-plan.qut.edu.au/), or ask your project lead/eResearch. Add `#PBS -P ABCDEF1234` to the directive block (use your real RPID), or submit with:

```bash
export AQUA_RPID=ABCDEF1234  # replace with your authorized project RPID
qsub -P "$AQUA_RPID" job.pbs
```

Do not put `$AQUA_RPID` in a `#PBS` directive: PBS does not expand shell variables there. See [RPID/PBS instructions](skills/aqua-hpc/references/pbs.md) and [source/verification notes](skills/aqua-hpc/references/sources.md).

## Getting started with AI coding agents

For both Codex and Claude Code, start with [AI4Coding’s practical tips](https://margauxmedwards.github.io/ai4coding/) on context, prompts and defining success. The [AI4Coding repository](https://github.com/margauxmedwards/ai4coding) contains the presentation and supporting material. Then install the Aqua skill below.

## Install for your agent

Clone this repo locally, then install into the project where you work:

```bash
git clone https://github.com/margauxmedwards/aqua-hpc-skills.git
cd aqua-hpc-skills
python3 scripts/install_skills.py --agent codex --project /path/to/project
python3 scripts/install_skills.py --agent claude --project /path/to/project
# Optional: --agent copilot installs the same skill under .github/skills.
```

The installer copies the self-contained skill and references to `.agents/skills/aqua-hpc` (Codex), `.claude/skills/aqua-hpc` (Claude), or `.github/skills/aqua-hpc` (Copilot). It refuses to overwrite an existing installation. Compare updates and remove/move the old copy deliberately before reinstalling. It does not modify personal agent settings or grant SSH access. Reload the agent session if needed.

Codex prompt: `$aqua-hpc Prepare a PBS array for this CLI, varying sensors and models. Inspect its flags and Pixi environment; stage a smoke case and show the resource request before submission.`

Claude Code prompt: `/aqua-hpc Diagnose these failed array cells, verify the runtime code and expected outputs, and prepare a bounded retry of only missing results.`

For either agent: supply your SSH alias, remote paths, authorized RPID, intended actions and resource/concurrency budget. The agent can run locally and use SSH; installing an agent on a compute node is not required. See [agent workflows](docs/agent-workflows.md).

## Try the portable example

The [CPU matrix example](examples/matrix/README.md) exercises explicit flags, bounded arrays, per-cell outputs, and completeness checks with Python's standard library. It has a preview mode and requires `--submit` plus a real RPID for PBS submission. It does not need ROS, a GPU, Pixi or private data.

## Read only what you need

| Topic | Guide |
| --- | --- |
| Common requests and response templates | [Request cookbook](skills/aqua-hpc/references/common-requests.md) |
| QCR versus general, walltime versus queue wait | [Queue/time selection](skills/aqua-hpc/references/queue-and-time.md) |
| Error fixes and RAM/walltime retries | [Bounded recovery](skills/aqua-hpc/references/recovery.md) |
| Accounting, resources, queues and PBS | [PBS](skills/aqua-hpc/references/pbs.md) |
| Pixi tasks, lockfiles, runtime verification | [Environments](skills/aqua-hpc/references/environments.md) |
| Flag-driven experiments and complete results | [Experiments](skills/aqua-hpc/references/experiments.md) |
| ROS builds, DDS isolation and playback | [ROS](skills/aqua-hpc/references/ros.md) |
| SSH, transfer, recovery and offline tracking | [Operations](skills/aqua-hpc/references/operations.md) |

## Migration and contribution

The former `.github/copilot/skills/*.md` paths now point to the maintained skill. Replace old copied instructions; do not load both generations. Legacy smoke helpers intentionally stop with migration instructions instead of retaining rapid SSH polling or automatic uploads.

Run `python3 -m unittest discover -s tests -v` before contributing code. The [behavioral evaluation fixtures](tests/behavior/README.md) exercise common requests against Codex and Claude without submitting real jobs. Keep examples generic and small; never commit credentials, private paths/data, real RPIDs or raw job environment dumps. Record dates and evidence for site-specific claims. This update's scripts are locally tested with mocked PBS; an authorized RPID submission remains a user/site validation step.

Released under the [MIT license](LICENSE).
