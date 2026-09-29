# Reproducible environments with Pixi

Pixi brings dependency resolution, a lockfile, named environments and repeatable tasks into the repository. It is useful for Python, native libraries and supported RoboStack environments; it is not required for workloads already using a maintained module or container setup.

Commit `pixi.toml` and `pixi.lock` together. Record `pixi --version` on both machines: older executables may not understand a newer manifest or lock format. Pin the team's tested Pixi version in setup/CI; no single historical Aqua version is a permanent requirement.

```bash
pixi --version
pixi install --locked
pixi run --locked python -c 'import sys; print(sys.executable)'
pixi run --locked experiment --sensor camera --model baseline --seed 0
```

Prepare dependencies in an environment with permitted network access before a large array. Heavy builds still belong in scheduled resources. `--locked` checks manifest/lock consistency; it does not promise no installation or network access. `--frozen` uses the lock without checking freshness, so it is not a substitute for consistency validation. Check the installed version's help before choosing offline/no-install modes. Never have an entire array solve or mutate the same shared environment concurrently.

For a pre-provisioned environment, smoke-test imports and the actual command under the same activation used by PBS. Do not copy workstation `.pixi`, virtualenv, `build/`, or `install/` directories to a different machine as if they were portable. Rebuild native extensions for the target architecture and ABI. Use approved containers when appropriate and record the image digest plus bind mounts.

Activation can override variables passed with `qsub -v`. Check selected effective values **inside** `pixi run`, especially `ROS_DOMAIN_ID`, thread limits and application flags. Avoid nested activation when already inside the correct environment. Prefer explicit argv/configuration over a web of inherited shell settings.

For GPU workloads, log device model, driver, framework version and perform a real device operation. Import success alone misses incompatible CUDA kernels. A virtual-package override used to resolve an environment without a GPU does not supply a driver or make runtime GPU execution valid.

Task sketch (merge into an existing manifest; resolve and commit its lock before use):

```toml
[tasks]
experiment = "python scripts/run_experiment.py"
build = "colcon build --symlink-install"
```

Use `pixi run --locked experiment --help` to confirm forwarded flags. Keep model weights and datasets outside the environment and identify them by version/checksum.
