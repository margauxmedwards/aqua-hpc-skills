from pathlib import Path
import tempfile
import unittest
from scripts.prepare_pages import prepare
from scripts.check_site import check


class PagesTests(unittest.TestCase):
    def test_stages_public_guide_and_references_only(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = prepare(Path(temporary)/'source')
            guide = (root/'index.html').read_text()
            self.assertNotIn('href="../', guide)
            self.assertIn('href="first-job.html"', guide)
            for name in ('first-job.html', 'agents.html', 'rpid.html', 'walltime.html', 'mount.html', 'ros.html', 'notify.html'):
                page = (root/name).read_text()
                self.assertNotIn('href="../', page, name)
                self.assertIn('href="index.html"', page, name)
            self.assertIn('href="skills/aqua-hpc/references/ros.html"', (root/'ros.html').read_text())
            self.assertTrue((root/'guide.css').is_file())
            self.assertTrue((root/'guide.js').is_file())
            self.assertNotIn('git switch refresh-agent-hpc-workflows', guide)
            self.assertFalse((root/'.github').exists())
            self.assertFalse((root/'scripts').exists())
            self.assertFalse((root/'tests/test_workflows.py').exists())
            ref = (root/'skills/aqua-hpc/references/pbs.md').read_text()
            self.assertTrue(ref.startswith('---\nlayout: reference\n'))
            self.assertIn('sources.html', ref)
            self.assertIn('../../../index.html', ref)
            with self.assertRaises(ValueError):
                prepare(root)

    def test_checker_handles_subpaths_and_detects_broken_links(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root/'refs').mkdir()
            (root/'index.html').write_text('<a href="refs/topic.html#detail">Topic</a>')
            (root/'refs/topic.html').write_text('<h1 id="detail">Topic</h1><a href="../index.html">Guide</a>')
            self.assertEqual(check(root), 2)
            (root/'refs/topic.html').write_text('<h1>Missing target</h1>')
            with self.assertRaises(AssertionError):
                check(root)
            (root/'index.html').write_text('<a href="/refs/topic.html">Broken on project site</a>')
            with self.assertRaises(AssertionError):
                check(root)


if __name__ == '__main__':
    unittest.main()
