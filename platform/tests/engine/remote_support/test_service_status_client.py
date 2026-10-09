import subprocess
import unittest
from unittest.mock import patch

from src.engine.remote_support.service_status_client import RustDeskServiceStatusClient


class ServiceStatusTests(unittest.TestCase):
    def test_enabled_but_failed_is_not_reported_as_active(self):
        with patch('subprocess.run', return_value=subprocess.CompletedProcess(
            [], 0, 'LoadState=loaded\nActiveState=failed\nUnitFileState=enabled\n',
        )) as run:
            status = RustDeskServiceStatusClient().status()
        self.assertEqual(status, {'enabled': True, 'active': False, 'service_state': 'failed'})
        self.assertEqual(run.call_args.kwargs['timeout'], 2)

    def test_missing_service_and_timeout_are_reported(self):
        with patch('subprocess.run', return_value=subprocess.CompletedProcess([], 0, 'LoadState=not-found\n')):
            with self.assertRaisesRegex(RuntimeError, 'not installed'):
                RustDeskServiceStatusClient().status()
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired('systemctl', 2)):
            with self.assertRaisesRegex(RuntimeError, 'unavailable'):
                RustDeskServiceStatusClient().status()
