"""Keep standalone guide navigation, source links and field labels intact."""
from html.parser import HTMLParser
from pathlib import Path
import unittest
import os
import subprocess
import tempfile
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class GuideParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.links = []
        self.fields = []
        self.labels = []
        self.copy_targets = []
        self.code_blocks = {}
        self.current_code = None

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'a' and 'href' in attrs:
            self.links.append(attrs['href'])
        if tag in ('input', 'select', 'textarea'):
            self.fields.append(attrs.get('id'))
        if tag == 'label':
            self.labels.append(attrs.get('for'))
        if tag == 'code' and 'id' in attrs:
            self.current_code = attrs['id']
            self.code_blocks[self.current_code] = ''
        if 'data-copy' in attrs:
            self.copy_targets.append(attrs['data-copy'])

    def handle_data(self, data):
        if self.current_code:
            self.code_blocks[self.current_code] += data

    def handle_endtag(self, tag):
        if tag == 'code':
            self.current_code = None


class GuideTests(unittest.TestCase):
    def test_beginner_job_script_produces_the_documented_result(self):
        parser = GuideParser()
        parser.feed((ROOT/'docs/first-job.html').read_text())
        with tempfile.TemporaryDirectory() as temporary:
            subprocess.run(['bash', '-c', parser.code_blocks['hello-pbs-script']],
                           cwd=temporary, check=True, capture_output=True, text=True)
            result = subprocess.run(['bash', 'hello.pbs'], cwd=temporary, check=True,
                                    capture_output=True, text=True,
                                    env=dict(os.environ, PBS_O_WORKDIR=temporary, PBS_JOBID='123.test'))
            self.assertIn('CPU arithmetic PASS: 5000050000', result.stdout)
            self.assertIn('Job: 123.test', result.stdout)
            self.assertEqual((Path(temporary)/'result.txt').read_text(), result.stdout)

    def test_beginner_submission_passes_rpid_and_rejects_placeholder(self):
        parser = GuideParser()
        parser.feed((ROOT/'docs/first-job.html').read_text())
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            qsub = root/'qsub'
            qsub.write_text('#!/bin/sh\nprintf "%s\\n" "$@" > "$RECORD"\nprintf "123.test\\n"\n')
            qsub.chmod(0o755)
            record = root/'arguments.txt'
            environment = dict(os.environ, PATH=str(root)+os.pathsep+os.environ['PATH'], RECORD=str(record))
            result = subprocess.run(['bash', '-c', parser.code_blocks['first-submit']],
                                    cwd=root, env=environment, input='TESTXX0000\n',
                                    capture_output=True, text=True, check=True)
            self.assertIn('123.test', result.stdout)
            self.assertEqual(record.read_text().splitlines(),
                             ['-P', 'TESTXX0000', '-o', str(root/'job.log'), 'hello.pbs'])
            record.unlink()
            for invalid in ['ABCDEF1234', 'invalid']:
                subprocess.run(['bash', '-c', parser.code_blocks['first-submit']],
                               cwd=root, env=environment, input=invalid+'\n',
                               capture_output=True, text=True, check=True)
                self.assertFalse(record.exists(), 'Placeholder must not reach qsub')

    def test_home_links_every_guide_and_official_docs(self):
        parser = GuideParser()
        parser.feed((ROOT/'docs/index.html').read_text())
        for page in ('first-job.html', 'agents.html', 'rpid.html', 'walltime.html', 'mount.html',
                     'notify.html', 'ros.html', 'https://docs.eres.qut.edu.au/about-aqua'):
            self.assertIn(page, parser.links)
        self.assertEqual(parser.fields, [], 'Home page should link to helpers, not embed them')

    def test_status_file_snippet_records_start_and_exit_code(self):
        parser = GuideParser()
        parser.feed((ROOT/'docs/mount.html').read_text())
        with tempfile.TemporaryDirectory() as temporary:
            script = ('set -euo pipefail\ncd "$PBS_O_WORKDIR"\n' + parser.code_blocks['status-job'] +
                      '\necho work\nexit 3\n')
            result = subprocess.run(['bash', '-c', script], capture_output=True, text=True,
                                    env=dict(os.environ, PBS_O_WORKDIR=temporary, PBS_JOBID='123.test'))
            self.assertEqual(result.returncode, 3)
            lines = (Path(temporary)/'status.txt').read_text().splitlines()
            self.assertTrue(lines[0].startswith('running 123.test '), lines)
            self.assertTrue(lines[1].startswith('finished exit=3 '), lines)

    def test_gpu_model_is_an_option_not_a_default(self):
        parser = GuideParser()
        parser.feed((ROOT/'docs/first-job.html').read_text())
        select = [line for line in parser.code_blocks['gpu-select'].splitlines() if line.startswith('#PBS')]
        self.assertEqual(len(select), 3)
        self.assertNotIn('gpu_id', select[0])
        self.assertTrue(select[1].endswith(':gpu_id=A100'))
        self.assertTrue(select[2].endswith(':gpu_id=H100'))

    def test_helpers_live_on_their_own_pages(self):
        pages = {}
        for name in ('first-job.html', 'rpid.html', 'walltime.html'):
            pages[name] = GuideParser()
            pages[name].feed((ROOT/'docs'/name).read_text())
        self.assertIn('rpid-form', pages['rpid.html'].ids)
        self.assertIn('walltime-form', pages['walltime.html'].ids)
        self.assertNotIn('rpid-form', pages['first-job.html'].ids)
        self.assertNotIn('walltime-form', pages['first-job.html'].ids)
        self.assertIn('rpid.html', pages['first-job.html'].links)
        self.assertIn('walltime.html', pages['first-job.html'].links)

    def test_agent_guide_links_basics_and_official_docs_without_walkthrough(self):
        parser = GuideParser()
        parser.feed((ROOT/'docs/agents.html').read_text())
        self.assertIn('first-job.html', parser.links)
        self.assertIn('https://docs.eres.qut.edu.au/about-aqua', parser.links)
        self.assertNotIn('hello-pbs-script', parser.code_blocks)
        basics = GuideParser()
        basics.feed((ROOT/'docs/first-job.html').read_text())
        self.assertIn('agents.html', basics.links)
        self.assertIn('https://docs.eres.qut.edu.au/hpc-submitting-jobs-on-aqua', basics.links)

    def test_navigation_links_copy_targets_and_labels(self):
        parsed = {}
        for path in sorted((ROOT/'docs').glob('*.html')):
            name = path.name
            text = path.read_text()
            self.assertIn('aria-label="Site"', text, f'Missing site navigation in {name}')
            self.assertNotIn('{ind(', text, f'Unrendered template placeholder in {name}')
            self.assertNotIn('</>', text, f'Malformed closing tag in {name}')
            parsed[name] = GuideParser()
            parsed[name].feed(text)
        for name, parser in parsed.items():
            with self.subTest(page=name):
                self.assertEqual(len(parser.ids), len(set(parser.ids)), 'Duplicate HTML IDs')
                for target in parser.copy_targets:
                    self.assertIn(target, parser.ids, 'Broken copy target')
                for field in parser.fields:
                    self.assertIsNotNone(field)
                    self.assertIn(field, parser.labels, 'Unlabelled form field')
                for href in parser.links:
                    parts = urlsplit(href)
                    if parts.scheme or parts.netloc:
                        continue
                    if parts.path:
                        self.assertTrue((ROOT/'docs'/unquote(parts.path)).exists(), href)
                    target = parsed.get(parts.path or name)
                    if parts.fragment and target:
                        self.assertIn(unquote(parts.fragment), target.ids, href)

if __name__ == '__main__':
    unittest.main()
