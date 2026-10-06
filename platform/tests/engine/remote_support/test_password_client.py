import unittest
from unittest.mock import patch

from src.engine.remote_support.password_client import RustDeskPasswordClient


class PasswordClientTests(unittest.TestCase):
    def setUp(self):
        self.client = RustDeskPasswordClient('/test/ipc')
        self.password = ''
        self.options = {'keyboard':'enabled','approve-mode':'click'}
        self.reject_password = False
        self.preset = False
        self.calls = []

    def daemon(self, request):
        self.calls.append(request)
        kind, value = request['t'], request['c']
        if kind == 'Config':
            name, data = value
            if name == 'permanent-password-set':
                return {'t':kind,'c':[name,'Y' if self.password or self.preset else 'N']}
            if name == 'permanent-password' and data is not None:
                if not self.reject_password:
                    self.password = data
                return {'t':kind,'c':[name,'N' if self.reject_password else 'Y']}
        if kind == 'Options':
            if value is None:
                return {'t':kind,'c':dict(self.options)}
            self.options = dict(value)
            return {'t':kind,'c':None}
        self.fail('Unexpected operation')

    def test_setting_password_requires_ack_and_preserves_unrelated_options(self):
        with patch.object(self.client, '_exchange', side_effect=self.daemon):
            self.client.set_password('new-test-password')
            self.assertTrue(self.client.get_password_status()['unattended_enabled'])
        self.assertEqual(self.options['keyboard'], 'enabled')
        self.assertEqual(self.options['verification-method'], 'use-permanent-password')
        self.assertFalse(any(call.get('c', [None])[0] in ('permanent-password-storage-and-salt', 'permanent-password-is-preset') for call in self.calls if call['t']=='Config'))

    def test_rejected_change_does_not_enable_unattended_access(self):
        self.reject_password = True
        with patch.object(self.client, '_exchange', side_effect=self.daemon):
            with self.assertRaisesRegex(RuntimeError, 'rejected'):
                self.client.set_password('new-test-password')
        self.assertEqual(self.options['approve-mode'], 'click')

    def test_removal_disables_password_login_even_with_branded_preset(self):
        self.password = 'old-test-password'
        self.preset = True
        self.options['approve-mode'] = 'password'
        with patch.object(self.client, '_exchange', side_effect=self.daemon):
            self.client.remove_password()
            status = self.client.get_password_status()
        self.assertFalse(status['unattended_enabled'])
        self.assertTrue(status['configured'])
        self.assertEqual(self.options['approve-mode'], 'click')
        self.assertEqual(self.password, '')

    def test_ipc_failure_never_exposes_secret_in_error(self):
        with patch.object(self.client, '_exchange', side_effect=ValueError('private-test-value')):
            with self.assertRaises(RuntimeError) as error:
                self.client.set_password('private-test-value')
        self.assertNotIn('private-test-value', str(error.exception))
