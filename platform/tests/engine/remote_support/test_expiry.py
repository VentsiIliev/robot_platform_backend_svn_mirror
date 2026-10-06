import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from subprocess import CompletedProcess

from src.engine.remote_support import controller


class AccessExpiryTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.directory = Path(temp.name)
        self.marker = self.directory / 'enabled'
        self.active = False
        self.now = 1000.
        self.boot = self.directory / 'boot_id'
        self.boot.write_text('boot-one')
        for name, value in (('STATE_DIR', self.directory), ('ENABLE_MARKER', self.marker), ('BOOT_ID_PATH', self.boot)):
            patcher = patch.object(controller, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        for patcher in (patch.object(controller, '_elapsed_time', side_effect=lambda: self.now),
                        patch.object(controller.time, 'sleep'),
                        patch.object(controller, '_systemctl', side_effect=self.systemctl)):
            patcher.start()
            self.addCleanup(patcher.stop)

    def systemctl(self, *args):
        if args[0] == 'show':
            return CompletedProcess([], 0, 'LoadState=loaded\nActiveState=' + ('active' if self.active else 'inactive') + '\n', '')
        if args[0] == 'enable':
            self.assertTrue(controller._access_allowed())
            self.active = True
        if args[0] == 'stop':
            self.assertFalse(self.marker.exists())
            self.active = False
        return CompletedProcess([], 0, '', '')

    def test_every_preset_expires_without_a_gui_or_status_request(self):
        for duration in controller.ACCESS_DURATIONS:
            with self.subTest(duration=duration):
                controller.handle_request({'operation':'enable','duration_seconds':duration})
                self.assertEqual(controller._status()['remaining_seconds'], duration)
                self.now += duration - 1
                controller._expire_if_needed()
                self.assertTrue(self.active)
                self.now += 1
                controller._expire_if_needed()
                self.assertFalse(self.active)
                self.assertFalse(self.marker.exists())

    def test_controller_restart_and_repeated_enable_do_not_extend_deadline(self):
        controller.handle_request({'operation':'enable','duration_seconds':7200})
        window = json.loads(self.marker.read_text())
        self.now += 4000
        controller.handle_request({'operation':'enable','duration_seconds':18000})
        self.assertEqual(json.loads(self.marker.read_text()), window)
        self.assertEqual(controller._status()['remaining_seconds'], 3200)

    def test_reboot_and_legacy_marker_cannot_restart_remote_support(self):
        controller.handle_request({'operation':'enable'})
        self.boot.write_text('boot-two')
        self.assertFalse(controller._access_allowed())
        controller._expire_if_needed()
        self.assertFalse(self.active)
        self.marker.write_text('enabled\n')
        self.active = True
        controller._expire_if_needed()
        self.assertFalse(self.marker.exists())
        self.assertFalse(self.active)

    def test_failed_stop_is_retried_after_permission_marker_removed(self):
        controller.handle_request({'operation':'enable'})
        self.now += 900
        with patch.object(controller, '_systemctl', return_value=CompletedProcess([], 1, '', 'Stop failed')):
            with self.assertRaises(RuntimeError):
                controller._expire_if_needed()
        self.assertFalse(self.marker.exists())
        self.assertTrue((self.directory/'stop_pending').exists())
        controller._expire_if_needed()
        self.assertFalse(self.active)
        self.assertFalse((self.directory/'stop_pending').exists())

    def test_invalid_durations_and_extra_parameters_have_no_side_effects(self):
        for value in (0, -1, True, '900', 60, 7200.0):
            with self.subTest(value=value), self.assertRaises(ValueError):
                controller.handle_request({'operation':'enable','duration_seconds':value})
        for request in ({'operation':'disable','duration_seconds':900},
                        {'operation':'enable','duration_seconds':900,'command':'anything'},
                        {'operation':'status','password':'secret'}):
            with self.assertRaises(ValueError):
                controller.handle_request(request)
        self.assertFalse(self.marker.exists())
