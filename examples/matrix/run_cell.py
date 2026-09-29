#!/usr/bin/env python3
"""Execute one manifest row and validate its result before recording completion."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import subprocess
import sys


def load_manifest(path):
    rows = json.loads(Path(path).read_text())
    if not isinstance(rows, list) or not rows:
        raise ValueError('Manifest must be a nonempty list')
    ids = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != {'id', 'sensor', 'model', 'seed', 'samples'}:
            raise ValueError('Unexpected manifest fields')
        if not isinstance(row['id'], str) or not re.fullmatch(r'[a-zA-Z0-9_-]+', row['id']):
            raise ValueError('Unsafe cell ID')
        if row['id'] in ids:
            raise ValueError('Duplicate cell ID')
        ids.add(row['id'])
        if row['sensor'] not in ['camera', 'lidar'] or row['model'] not in ['baseline', 'alternate']:
            raise ValueError('Unsupported example combination')
        if type(row['seed']) is not int or type(row['samples']) is not int or row['samples'] <= 0:
            raise ValueError('Invalid seed/sample count')
    return rows


def validate(result, row):
    for key in ['sensor', 'model', 'seed', 'samples']:
        if result.get(key) != row[key]:
            raise ValueError(f'Output mismatch: {key}')
    metric = result.get('metric')
    if type(metric) not in (float, int) or not math.isfinite(metric):
        raise ValueError('Missing/nonfinite metric')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest', type=Path, required=True)
    p.add_argument('--index', type=int, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    rows = load_manifest(a.manifest)
    if not 0 <= a.index < len(rows):
        p.error('Index outside manifest')
    row = rows[a.index]
    cell = a.output / row['id']
    cell.mkdir(parents=True, exist_ok=False)  # refuse duplicate attempts/overwrites
    argv = [sys.executable, str(Path(__file__).with_name('experiment.py')),
            '--sensor', row['sensor'], '--model', row['model'], '--seed', str(row['seed']),
            '--samples', str(row['samples']), '--output', str(cell / 'result.json')]
    provenance = {'argv': argv, 'config': row, 'python': sys.executable,
                  'host': platform.node(), 'job_id': os.getenv('PBS_JOBID'),
                  'array_index': os.getenv('PBS_ARRAY_INDEX'),
                  'manifest_sha256': hashlib.sha256(a.manifest.read_bytes()).hexdigest()}
    (cell / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
    with (cell / 'stdout.log').open('w') as out, (cell / 'stderr.log').open('w') as err:
        subprocess.run(argv, check=True, stdout=out, stderr=err)
    result_path = cell / 'result.json'
    validate(json.loads(result_path.read_text()), row)
    complete = {'id': row['id'], 'validated': True,
                'result_sha256': hashlib.sha256(result_path.read_bytes()).hexdigest()}
    temporary = cell / 'complete.tmp'
    temporary.write_text(json.dumps(complete) + '\n')
    temporary.replace(cell / 'complete.json')
    print(f"Validated {row['id']}")


if __name__ == '__main__':
    main()
