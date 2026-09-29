#!/usr/bin/env python3
import os
import time

import wandb


def main() -> None:
    run = wandb.init(
        entity=os.getenv("WANDB_ENTITY"),
        project=os.getenv("WANDB_PROJECT", "qut-aqua"),
        job_type="smoke-test",
        config={"test": "wandb-smoke", "timestamp": int(time.time())},
    )

    for step in range(3):
        wandb.log({"smoke_metric": step * 0.5 + 1.0, "step": step}, step=step)

    wandb.summary["status"] = "ok"
    wandb.summary["host"] = os.uname().nodename
    run.finish()


if __name__ == "__main__":
    main()
