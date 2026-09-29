#!/usr/bin/env python3
"""Stage an isolated CPU demo and preview PBS submission; --submit opts in."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'examples' / 'matrix'))
from run_cell import load_manifest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run-dir', type=Path, required=True)
    p.add_argument('--manifest', type=Path, default=ROOT/'examples/matrix/matrix.json')
    p.add_argument('--rpid', default=os.getenv('AQUA_RPID'))
    p.add_argument('--concurrency', type=int, default=2)
    p.add_argument('--submit', action='store_true')
    a = p.parse_args()
    if not a.rpid or not re.fullmatch(r'[A-Z]{6}[0-9]{4}', a.rpid) or a.rpid == 'ABCDEF1234':
        p.error('Supply a real authorized RPID via --rpid or AQUA_RPID; example IDs are not accepted')
    if a.concurrency < 1:
        p.error('Concurrency must be positive')
    rows = load_manifest(a.manifest)
    run = a.run_dir.resolve()
    # PBS -v is comma-delimited and has its own parsing. Restrict this demo's path.
    if not re.fullmatch(r'/[A-Za-z0-9_./-]+', str(run)):
        p.error('Run path must be absolute and contain only letters, digits, _, ., / or -')
    if run.exists():
        p.error('Run directory already exists; use a new attempt path')
    run.mkdir(parents=True)
    source = ROOT/'examples/matrix'
    for name in ['job.pbs', 'experiment.py', 'run_cell.py', 'check_results.py']:
        shutil.copy2(source/name, run/name)
    (run/'matrix.json').write_text(json.dumps(rows, indent=2)+'\n')
    (run/'logs').mkdir()
    hashes = {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in run.iterdir() if f.is_file()}
    rev = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], capture_output=True, text=True)
    argv = ['qsub', '-P', a.rpid]
    if len(rows) > 1:
        argv += ['-J', f'0-{len(rows)-1}%{min(a.concurrency,len(rows))}']
    argv += ['-o', str(run/'logs')+'/', '-v', f'RUN_DIR={run}', str(run/'job.pbs')]
    record = {'state': 'prepared', 'argv': argv, 'source_commit': rev.stdout.strip() if rev.returncode == 0 else None,
              'staged_sha256': hashes, 'expected_cells': len(rows)}
    record_path = run/'submission.json'
    def save():
        temp = record_path.with_suffix('.tmp')
        temp.write_text(json.dumps(record, indent=2)+'\n')
        temp.replace(record_path)
    save()
    print(shlex.join(argv), flush=True)
    if not a.submit:
        print('Preview only. Snapshot prepared; no job submitted. Use the printed command on Aqua, or rerun with --submit and a NEW run directory.')
        return
    record['state'] = 'submitting'
    save()
    try:
        result = subprocess.run(argv, cwd=run, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as error:
        record.update(state='unknown', error=str(error))
        save()
        raise SystemExit('Submission unresolved; inspect submission.json and PBS before any retry')
    record.update(returncode=result.returncode, stdout=result.stdout, stderr=result.stderr)
    ids = [line.strip() for line in result.stdout.splitlines()
           if re.fullmatch(r'\d+(?:\[\])?\.[A-Za-z0-9_.-]+', line.strip())]
    if result.returncode != 0 or len(ids) != 1:
        record['state'] = 'unknown'
        save()
        raise SystemExit('No unambiguous successful submission; reconcile PBS before retrying')
    record.update(state='submitted', job_id=ids[0])
    save()
    print(f'Submitted {ids[0]}; execution and output validation remain pending.')


if __name__ == '__main__':
    main()
