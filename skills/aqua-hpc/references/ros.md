# ROS and headless robotics jobs

Preserve the project's ROS distribution, middleware and supported environment. Inspect `package.xml`, launch files, Pixi tasks and workspace setup scripts before changing them. Do not assume `/opt/ros/humble` exists on Aqua. Source the intended underlay and overlay within the job or its single environment activation.

Verify the code that actually runs: inspect resolved symlinks, `ros2 pkg prefix`, Python module `__file__`, and the executable's `--help`. Updating `src/` does not necessarily update a copied installation. Symlink installs can expose existing Python edits immediately, but new entry points, packaging changes and compiled code require a rebuild. Capture resolved paths in the smoke log.

Concurrent jobs on shared nodes can discover each other's DDS participants. Assign domains using a coordinated allocation appropriate to the ROS distribution, OS ephemeral-port range, middleware and participant count. A hash/modulo of job ID is not collision-free; one domain per job may still exhaust ports with many processes. Respect platform limits. For single-node workloads, consider supported localhost-only discovery, then verify actual isolation; localhost still spans jobs sharing that host. Multi-node jobs need a deliberately tested network configuration.

Inspect the effective domain and discovery settings after Pixi/container activation. A scheduler record proves what was submitted, not what reached the nodes. Avoid static activation settings that overwrite per-job isolation.

Use readiness/acknowledgement checks before playback, bounded startup and inactivity timeouts, and explicit child-process error propagation. A short-lived latched/transient-local publisher can disappear before a slow model finishes loading; keep readiness signals alive until the intended consumers acknowledge them. Track child PIDs and clean up only processes owned by the run.

Bag timestamps, clock source, playback rate, QoS and topic remappings belong in the saved configuration. Check expected messages/results per sensor and alignment coverage. Diagnose observed skip reasons and publisher/subscriber counts before blaming middleware. Test a minimal pub/sub pair within the allocated environment when transport is in doubt.
