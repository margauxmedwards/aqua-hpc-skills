import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT/'examples/matrix'


def call(*args, **kwargs):
    return subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True, **kwargs)


class Workflows(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='aqua-test-')
        self.base = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def cell(self, index):
        return call(DEMO/'run_cell.py', '--manifest', DEMO/'matrix.json',
                    '--index', index, '--output', self.base/'results')

    def check(self):
        return call(DEMO/'check_results.py', '--manifest', DEMO/'matrix.json',
                    '--output', self.base/'results')

    def test_missing_success_duplicate_and_tamper(self):
        self.assertNotEqual(self.check().returncode, 0)
        for i in range(8):
            result = self.cell(i)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.check().returncode, 0)
        self.assertNotEqual(self.cell(0).returncode, 0)
        result_path = self.base/'results/camera-baseline-0/result.json'
        data = json.loads(result_path.read_text())
        data['metric'] = float('nan')
        result_path.write_text(json.dumps(data))
        self.assertNotEqual(self.check().returncode, 0)

    def test_invalid_index_and_manifest_do_not_create_results(self):
        self.assertNotEqual(self.cell(-1).returncode, 0)
        self.assertNotEqual(self.cell(8).returncode, 0)
        bad = self.base/'bad.json'
        rows = json.loads((DEMO/'matrix.json').read_text())
        rows[0]['id'] = '../escape'
        bad.write_text(json.dumps(rows))
        result = call(DEMO/'run_cell.py', '--manifest', bad, '--index', 0,
                      '--output', self.base/'results')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.base/'results').exists())

    def test_failed_child_never_emits_completion(self):
        import shutil
        source = self.base/'source'
        shutil.copytree(DEMO, source)
        (source/'experiment.py').write_text('raise SystemExit(7)\n')
        result = call(source/'run_cell.py', '--manifest', source/'matrix.json',
                      '--index', 0, '--output', self.base/'results')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.base/'results/camera-baseline-0/complete.json').exists())

    def submit(self, path, *extra, env=None):
        # Synthetic format-valid ID only for local tests; never sent to real PBS.
        return call(ROOT/'scripts/submit_demo.py', '--run-dir', path,
                    '--rpid', 'TESTXX0000', *extra, env=env)

    def test_preview_stages_snapshot_without_qsub(self):
        run = self.base/'preview'
        result = self.submit(run)
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads((run/'submission.json').read_text())
        self.assertEqual(record['state'], 'prepared')
        self.assertEqual(record['expected_cells'], 8)
        self.assertIn('matrix.json', record['staged_sha256'])
        self.assertNotEqual(self.submit(run).returncode, 0)

    def test_single_row_uses_plain_job(self):
        manifest = self.base/'single.json'
        manifest.write_text(json.dumps(json.loads((DEMO/'matrix.json').read_text())[:1]))
        run = self.base/'single'
        result = self.submit(run, '--manifest', manifest)
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads((run/'submission.json').read_text())
        self.assertNotIn('-J', record['argv'])

    def test_rpid_and_path_validation(self):
        for rpid in ['ABCDEF1234', 'bad', 'TESTXX0000;echo']:
            result = call(ROOT/'scripts/submit_demo.py', '--run-dir', self.base/'bad', '--rpid', rpid)
            self.assertNotEqual(result.returncode, 0)
        self.assertNotEqual(self.submit(self.base/'bad,path').returncode, 0)
        self.assertFalse((self.base/'bad').exists())

    def test_qsub_success_and_unknown_are_recorded(self):
        bin_path = self.base/'bin'
        bin_path.mkdir()
        qsub = bin_path/'qsub'
        env = dict(os.environ, PATH=str(bin_path)+os.pathsep+os.environ['PATH'])
        for index, (body, expected) in enumerate([
            ('echo "123[].aqua"', 'submitted'),
            ('echo "scheduler unavailable" >&2; exit 1', 'unknown'),
            ('exit 0', 'unknown'),
        ]):
            qsub.write_text('#!/bin/sh\n'+body+'\n')
            qsub.chmod(0o755)
            run = self.base/f'run{index}'
            result = self.submit(run, '--submit', env=env)
            record = json.loads((run/'submission.json').read_text())
            self.assertEqual(record['state'], expected)
            self.assertEqual(result.returncode == 0, expected == 'submitted')
            self.assertEqual(record['argv'][1:3], ['-P', 'TESTXX0000'])

    def test_installer_keeps_existing_files(self):
        for agent, location in [('codex', '.agents'), ('claude', '.claude'), ('copilot', '.github')]:
            result = call(ROOT/'scripts/install_skills.py', '--agent', agent, '--project', self.base)
            self.assertEqual(result.returncode, 0, result.stderr)
            skill = self.base/location/'skills/aqua-hpc/SKILL.md'
            skill.write_text('local customization\n')
            result = call(ROOT/'scripts/install_skills.py', '--agent', agent, '--project', self.base)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(skill.read_text(), 'local customization\n')


if __name__ == '__main__':
    unittest.main()
