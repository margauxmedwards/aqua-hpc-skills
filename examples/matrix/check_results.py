#!/usr/bin/env python3
"""Fail if any expected cell is missing, invalid, or changed after validation."""
import argparse
import hashlib
import json
from pathlib import Path
from run_cell import load_manifest, validate


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    rows = load_manifest(a.manifest)
    failures = []
    for row in rows:
        cell = a.output / row['id']
        try:
            result_path = cell / 'result.json'
            validate(json.loads(result_path.read_text()), row)
            complete = json.loads((cell / 'complete.json').read_text())
            if (complete.get('validated') is not True or complete.get('id') != row['id'] or
                    complete.get('result_sha256') != hashlib.sha256(result_path.read_bytes()).hexdigest()):
                raise ValueError('Completion record does not match result')
            provenance = json.loads((cell / 'provenance.json').read_text())
            if (provenance.get('config') != row or provenance.get('manifest_sha256') !=
                    hashlib.sha256(a.manifest.read_bytes()).hexdigest()):
                raise ValueError('Provenance does not match manifest')
        except (OSError, ValueError, TypeError, AttributeError) as error:
            failures.append({'id': row['id'], 'error': str(error)})
    print(json.dumps({'expected': len(rows), 'validated': len(rows)-len(failures),
                      'failures': failures}, indent=2))
    return bool(failures)


if __name__ == '__main__':
    raise SystemExit(main())
