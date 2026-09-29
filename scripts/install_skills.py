#!/usr/bin/env python3
"""Install a self-contained skill without replacing existing user content."""
import argparse
from pathlib import Path
import shutil


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--agent', choices=['codex', 'claude', 'copilot'], required=True)
    parser.add_argument('--project', type=Path, required=True)
    args = parser.parse_args()
    locations = {'codex': '.agents', 'claude': '.claude', 'copilot': '.github'}
    project = args.project.resolve()
    if not project.is_dir():
        parser.error('Project directory must already exist')
    destination = project / locations[args.agent] / 'skills' / 'aqua-hpc'
    if destination.exists() or destination.is_symlink():
        parser.error(f'Refusing to replace existing skill: {destination}')
    source = Path(__file__).resolve().parents[1] / 'skills' / 'aqua-hpc'
    shutil.copytree(source, destination)
    print(destination)


if __name__ == '__main__':
    main()
