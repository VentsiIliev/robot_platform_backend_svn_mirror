"""Real local SVN feed reads plus bounded and timed-out subprocesses."""
from dataclasses import replace
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from src.engine.updates.config import UpdateConfig
from src.engine.updates.svn_source import fetch


@unittest.skipUnless(shutil.which('svn') and shutil.which('svnadmin'), 'SVN tools unavailable')
class SVNSourceTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        self.repository = self.root / 'svn'
        subprocess.run(['svnadmin', 'create', str(self.repository)], check=True)
        source = self.root / 'source'
        source.mkdir()
        (source / 'latest.json').write_bytes(b'{"version":"1.0.0"}')
        subprocess.run(['svn', 'import', '--non-interactive', '-m', 'local test fixture', str(source),
                        self.repository.as_uri()], check=True, stdout=subprocess.DEVNULL)
        self.config = UpdateConfig(self.root / 'installed', 'https://svn.example/feed/', None,
                                   repository_type='svn', timeout_seconds=5)
        self.url = self.repository.as_uri() + '/latest.json'
        self.target = self.root / 'download'

    def test_reads_versioned_feed_file(self):
        fetch(self.config, self.url, self.target, 1024)
        self.assertEqual(self.target.read_bytes(), b'{"version":"1.0.0"}')

    def test_download_limit_is_enforced(self):
        with self.assertRaisesRegex(ValueError, 'limit exceeded'):
            fetch(self.config, self.url, self.target, 4)

    def test_missing_versioned_file_reports_error(self):
        with self.assertRaisesRegex(ValueError, 'SVN update download failed'):
            fetch(self.config, self.url + '-missing', self.target, 1024)

    def test_timeout_terminates_subprocess(self):
        original = subprocess.Popen
        processes = []
        def sleeper(args, **kwargs):
            process = original([sys.executable, '-c', 'import time; time.sleep(5)'], **kwargs)
            processes.append(process)
            return process
        with patch('src.engine.updates.svn_source.subprocess.Popen', side_effect=sleeper):
            with self.assertRaises(TimeoutError):
                fetch(replace(self.config, timeout_seconds=0.1), self.url, self.target, 1024)
        self.assertIsNotNone(processes[0].poll())
