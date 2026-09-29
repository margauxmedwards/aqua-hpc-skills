# Sources and maintenance

Last reviewed: 28 September 2026. This is a community toolkit for QCR users, not official QUT policy or a service operated by QUT.

- [QUT submitting jobs, step 5](https://docs.eres.qut.edu.au/hpc-submitting-jobs-on-aqua)
- [QUT RDSS](https://docs.eres.qut.edu.au/about-rdss) and [FAQs](https://docs.eres.qut.edu.au/rdss-faqs)
- [QUT DMP / RPID lookup](https://data-mgmt-plan.qut.edu.au/)

Those QUT pages were inaccessible to the documentation browser during this update. The 2 November 2026 enforcement date comes from a user-supplied QUT notice; RPID syntax/format and the temporary transition behavior were observed in a live Aqua PBS notice on 28 September. Exact DMP UI steps and project authorization were not tested. Recheck official guidance before relying on dates, quotas or resource labels.

Packaging and environment references checked during this update:

- [Codex skill locations](https://developers.openai.com/codex/skills)
- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Pixi run](https://pixi.prefix.dev/latest/reference/cli/pixi/run/) and [install](https://pixi.prefix.dev/latest/reference/cli/pixi/install/)
- [ROS domain ID background](https://docs.ros.org/en/rolling/Concepts/Intermediate/About-Domain-ID.html) (browser access blocked; use your installed distribution's documentation)

Operational lessons were generalized from local agent-assisted PBS campaigns and locally improved skill references: environment/version drift, installed-code verification, SSH overload, queue placement, right-sizing, atomic output validation, recovery and ROS activation/isolation. Historical failures are diagnostic hypotheses, not universal cluster facts. No private datasets, experiment results, project RPIDs, credentials or personal cluster paths are required by the toolkit.

A further read-only live check on 28 September 2026 inspected `qstat -Qf qcr-users cpu_batch gpu_batch` and selected `pbsnodes -av` resource fields. The [queue/time guide](queue-and-time.md) records the relevant routing, ACL and limit observations. No QCR job was submitted and no user entitlement was inferred from queue visibility.
