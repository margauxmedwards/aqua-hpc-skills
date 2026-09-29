#!/usr/bin/env python3
"""Tiny deterministic flag-driven CPU workload; no scientific claims."""
import argparse
import json
import math
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sensor', choices=['camera', 'lidar'], required=True)
    p.add_argument('--model', choices=['baseline', 'alternate'], required=True)
    p.add_argument('--seed', type=int, required=True)
    p.add_argument('--samples', type=int, default=10)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.samples <= 0:
        p.error('--samples must be positive')
    metric = sum(math.sin(i + a.seed) ** 2 for i in range(a.samples)) / a.samples
    result = dict(sensor=a.sensor, model=a.model, seed=a.seed,
                  samples=a.samples, metric=metric)
    # The orchestrator supplies a unique attempt directory.
    temporary = a.output.with_suffix('.tmp')
    temporary.write_text(json.dumps(result) + '\n')
    temporary.replace(a.output)


if __name__ == '__main__':
    main()
