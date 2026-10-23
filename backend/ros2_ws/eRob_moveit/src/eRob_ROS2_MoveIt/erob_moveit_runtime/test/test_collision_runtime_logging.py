"""Exercise diagnostic callback changes without starting ROS or real hardware."""
import ast
import json
from pathlib import Path
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock


def callbacks():
    script = Path(__file__).resolve().parent.parent / "robot_controller.py"
    if not script.exists():
        script = Path(__file__).resolve().parents[1] / "scripts" / "robot_controller.py"
    tree = ast.parse(script.read_text())
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "RobotController")
    methods = [node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name in {
        "_collision_runtime_context", "_collision_monitor_stop_callback", "_collision_monitor_state_callback",
        "_collision_monitor_config_callback",
        "reset_motion_interlock", "_startup_auto_enable_drives_loop",
        "is_hardware_ready_for_drive_enable",
        "is_hardware_ready_for_motion", "get_hardware_fault_reason", "get_motion_interlock_status",
    }]
    module = ast.fix_missing_locations(ast.Module(body=methods, type_ignores=[]))
    namespace = {"json": json, "time": time, "String": SimpleNamespace, "DynamicJointState": SimpleNamespace,
                 "config": SimpleNamespace(COLLISION_RESET_RECALIBRATE_ON_RELEASE=False)}
    exec(compile(module, str(script), "exec"), namespace)
    return namespace


class TestCollisionRuntimeLogging(unittest.TestCase):
    def setUp(self):
        self.methods = callbacks()
        self.logger = MagicMock()
        self.robot = SimpleNamespace(
            _motion_interlock_lock=threading.Lock(),
            _collision_last_reset_completed_monotonic_ns=time.monotonic_ns() - 50000000,
            _motion_interlock_active=False, _collision_recovery_hold=False,
            _collision_detection_suppressed=False, _collision_monitor_ready=True,
            _collision_monitor_state_ts=time.monotonic(), is_executing=True,
            _collision_monitor_acknowledgements=0, _collision_monitor_baseline_valid=True,
            last_submitted_task_id=123, get_logger=lambda: self.logger,
            get_drive_operation_status=MagicMock(return_value={"requested_enabled": True}),
            trip_motion_interlock=MagicMock(), stop_motion=MagicMock(return_value={"success": True}),
            collision_stop=MagicMock(return_value={"success": True}),
        )
        self.robot._collision_runtime_context = lambda: self.methods["_collision_runtime_context"](self.robot)

    def test_recovery_config_changes_use_ros_logger_signature(self):
        # Autospec the actual ROS signature so MagicMock cannot hide a callback crash.
        from rclpy.impl.rcutils_logger import RcutilsLogger
        from unittest.mock import create_autospec
        self.logger = create_autospec(RcutilsLogger, instance=True)
        callback = self.methods["_collision_monitor_config_callback"]
        for suppressed, label in ((True, "ENABLED"), (False, "disabled")):
            with self.subTest(suppressed=suppressed):
                callback(self.robot, SimpleNamespace(data=json.dumps({
                    "collision_detection_suppressed": suppressed,
                })))
                self.assertEqual(self.robot._collision_detection_suppressed, suppressed)
                self.logger.warning.assert_called_with(
                    "[CollisionRecovery] Recovery-only motion mode " + label)
        self.assertEqual(self.logger.warning.call_count, 2)

    def test_unchanged_or_invalid_recovery_config_does_not_log(self):
        callback = self.methods["_collision_monitor_config_callback"]
        for data in ('{}', '{"collision_detection_suppressed": false}', '[]', 'bad json'):
            callback(self.robot, SimpleNamespace(data=data))
        self.assertFalse(self.robot._collision_detection_suppressed)
        self.logger.warning.assert_not_called()

    def prepare_startup(self):
        self.robot._fake_hardware = False
        self.robot._ethercat_fault_lock = threading.Lock()
        self.robot._ethercat_motion_fault = False
        self.robot._ethercat_fault_reason = "EtherCAT not operational"
        self.robot._motion_interlock_reason = "collision latched"
        self.robot._collision_monitor_ready = False
        self.robot.current_joint_state = SimpleNamespace()
        self.robot._get_controller_states = MagicMock(return_value={})
        self.robot.is_drive_operation_enabled_for_motion = MagicMock(return_value=False)

        def enable(enabled):
            self.robot.is_drive_operation_enabled_for_motion.return_value = True
            return {"success": True}

        self.robot.set_drive_operation_enabled = MagicMock(side_effect=enable)
        self.robot.is_hardware_ready_for_drive_enable = lambda: self.methods["is_hardware_ready_for_drive_enable"](self.robot)
        self.robot.is_hardware_ready_for_motion = lambda: self.methods["is_hardware_ready_for_motion"](self.robot)
        self.robot.get_hardware_fault_reason = lambda: self.methods["get_hardware_fault_reason"](self.robot)
        self.fake_clock(lambda now: None)
        self.methods.update({
            "STARTUP_AUTO_ENABLE_DRIVES_TIMEOUT_S": 0.3,
            "STARTUP_AUTO_ENABLE_DRIVES_RETRY_PERIOD_S": 0.1,
            "STARTUP_AUTO_ENABLE_DRIVES_VERIFY_TIMEOUT_S": 0.1,
            "rclpy": SimpleNamespace(ok=lambda: True),
        })

    def test_startup_enables_drives_before_observer_ready_but_keeps_motion_blocked(self):
        self.prepare_startup()
        self.assertFalse(self.robot.is_hardware_ready_for_motion())
        self.methods["_startup_auto_enable_drives_loop"](self.robot)
        self.robot.set_drive_operation_enabled.assert_called_once_with(True)
        self.assertFalse(self.robot.is_hardware_ready_for_motion())
        self.logger.error.assert_not_called()

    def test_startup_does_not_enable_drives_with_ethercat_fault(self):
        self.prepare_startup()
        self.robot._ethercat_motion_fault = True
        self.methods["_startup_auto_enable_drives_loop"](self.robot)
        self.robot.set_drive_operation_enabled.assert_not_called()
        self.logger.error.assert_called_once()

    def test_startup_does_not_enable_drives_with_latched_collision(self):
        self.prepare_startup()
        self.robot._motion_interlock_active = True
        self.methods["_startup_auto_enable_drives_loop"](self.robot)
        self.robot.set_drive_operation_enabled.assert_not_called()
        self.logger.error.assert_called_once()

    def test_startup_waits_for_joint_state_and_controller_services(self):
        self.prepare_startup()
        self.robot.current_joint_state = None
        self.methods["_startup_auto_enable_drives_loop"](self.robot)
        self.robot.set_drive_operation_enabled.assert_not_called()
        self.prepare_startup()
        self.robot._get_controller_states.return_value = None
        self.methods["_startup_auto_enable_drives_loop"](self.robot)
        self.robot.set_drive_operation_enabled.assert_not_called()

    def test_collision_preserves_event_id_and_captures_pre_stop_cached_state(self):
        self.methods["_collision_monitor_stop_callback"](self.robot, SimpleNamespace(data=json.dumps({
            "joint": "Joint_3", "detector": "cpp_realtime_dynamics", "diagnostic_event_id": 7,
        })))
        event = self.robot.last_collision_event
        self.assertEqual(event["diagnostic_event_id"], 7)
        self.assertEqual(event["runtime_context"]["last_submitted_task_id"], 123)
        self.assertTrue(event["runtime_context"]["is_executing"])
        self.assertFalse(event["runtime_context"]["detection_suppressed"])
        self.assertGreaterEqual(event["runtime_context"]["since_reset_complete_ms"], 50)
        self.robot.collision_stop.assert_called_once_with()
        self.robot.stop_motion.assert_not_called()

    def test_failed_diagnostic_capture_cannot_prevent_motion_stop(self):
        self.robot._collision_runtime_context = MagicMock(side_effect=RuntimeError("diagnostic unavailable"))
        self.methods["_collision_monitor_stop_callback"](self.robot, SimpleNamespace(data='{"joint":"Joint_2"}'))
        self.robot.trip_motion_interlock.assert_called_once()
        self.robot.collision_stop.assert_called_once_with()
        self.robot.stop_motion.assert_not_called()
        self.assertEqual(self.robot.last_collision_event["runtime_context_error"], "diagnostic unavailable")

    def test_readiness_logs_transitions_without_logging_every_telemetry_sample(self):
        sample = SimpleNamespace(interface_values=[SimpleNamespace(interface_names=["observer_ready"], values=[0.0])])
        callback = self.methods["_collision_monitor_state_callback"]
        callback(self.robot, sample)
        callback(self.robot, sample)
        self.logger.warning.assert_called_once()
        self.assertFalse(self.robot._collision_monitor_ready)

    def test_reset_logging_keeps_readiness_wait_and_records_completion_time(self):
        clock = SimpleNamespace(now=0.0)
        self.robot._motion_interlock_active = True
        self.robot._motion_interlock_reason = "collision"
        self.robot._collision_monitor_ready = False
        self.robot.last_collision_event = {"diagnostic_event_id": 7}
        self.robot._interlock_reset_unsafe_reason = lambda: None
        self.robot.runtime_adapter = SimpleNamespace(set_drive_operation_enabled=MagicMock(return_value={"success": True}))
        self.robot._collision_acknowledged_pub = SimpleNamespace(publish=MagicMock())

        def sleep(duration):
            self.assertTrue(self.robot._collision_recovery_hold)
            clock.now += duration
            self.robot._collision_monitor_ready = True
            self.robot._collision_monitor_state_ts = clock.now
            self.robot._collision_monitor_acknowledgements = 1

        self.methods["time"] = SimpleNamespace(
            monotonic=lambda: clock.now, monotonic_ns=lambda: int(clock.now * 1e9),
            time=lambda: 123.0 + clock.now, sleep=sleep,
        )
        result = self.methods["reset_motion_interlock"](self.robot)
        self.assertTrue(result["success"])
        self.assertFalse(self.robot._collision_recovery_hold)
        self.assertEqual(self.robot._collision_last_reset_completed_monotonic_ns, 50000000)
        self.assertIsNone(self.robot.last_collision_event)
        entries = [json.loads(call.args[0].split('] ', 1)[1])
                   for call in self.logger.warning.call_args_list
                   if call.args[0].startswith('[CollisionRecoveryDiagnostics]')]
        self.assertEqual([entry["phase"] for entry in entries], ["reset_requested", "reset_completed"])
        self.assertEqual(entries[0]["previous_event_id"], 7)

    def prepare_reset(self):
        self.robot._motion_interlock_active = True
        self.robot._motion_interlock_reason = "original collision"
        self.robot.last_collision_event = {"diagnostic_event_id": 7}
        self.robot._interlock_reset_unsafe_reason = lambda: None
        self.robot.runtime_adapter = SimpleNamespace(set_drive_operation_enabled=MagicMock(return_value={"success": True}))
        self.robot._collision_acknowledged_pub = SimpleNamespace(publish=MagicMock())

    def fake_clock(self, on_sleep):
        clock = SimpleNamespace(now=0.0)

        def sleep(duration):
            clock.now += duration
            on_sleep(clock.now)

        self.methods["time"] = SimpleNamespace(
            monotonic=lambda: clock.now, monotonic_ns=lambda: int(clock.now * 1e9),
            time=lambda: 123.0 + clock.now, sleep=sleep,
        )
        return clock

    def test_timeout_records_joint_recovery_state_and_keeps_interlock(self):
        self.prepare_reset()
        sample = SimpleNamespace(interface_values=[SimpleNamespace(
            interface_names=["observer_ready", "baseline_valid", "acknowledgement_count",
                             "filtered_residual_nm", "release_limit_nm"],
            values=[0.0, 1.0, 1.0, 4.0, 3.0],
        )])

        def on_sleep(now):
            self.methods["_collision_monitor_state_callback"](self.robot, sample)

        self.fake_clock(on_sleep)
        result = self.methods["reset_motion_interlock"](self.robot)
        self.assertFalse(result["success"])
        self.assertIn("Joint_1 residual 4.000 Nm exceeds release limit 3.000 Nm", result["error"])
        self.assertTrue(self.robot._motion_interlock_active)
        self.assertFalse(self.robot._collision_recovery_hold)
        entries = [json.loads(call.args[0].split('] ', 1)[1])
                   for call in self.logger.warning.call_args_list]
        failure = next(entry for entry in entries if entry["phase"] == "reset_failed")
        self.assertEqual(failure["monitor_state"][0]["filtered_residual_nm"], 4.0)
        self.assertEqual(failure["monitor_state"][0]["release_limit_nm"], 3.0)
        self.assertIsNotNone(failure["runtime_context"]["monitor_state_age_ms"])

    def test_disable_during_recovery_fails_promptly_without_reenabling(self):
        self.prepare_reset()
        self.robot._collision_monitor_ready = False

        def on_sleep(now):
            self.robot.get_drive_operation_status.return_value = {"requested_enabled": False}

        clock = self.fake_clock(on_sleep)
        result = self.methods["reset_motion_interlock"](self.robot)
        self.assertFalse(result["success"])
        self.assertIn("drives were disabled during collision recovery", result["error"])
        self.assertLess(clock.now, 0.1)
        self.assertTrue(self.robot._motion_interlock_active)
        self.assertFalse(self.robot._collision_recovery_hold)
        self.robot.runtime_adapter.set_drive_operation_enabled.assert_called_once_with(self.robot, True)

    def test_stale_recovery_state_does_not_report_old_joint_blocker(self):
        self.prepare_reset()
        self.robot._collision_monitor_ready = False
        self.robot._collision_monitor_state_ts = 0.0
        self.robot._collision_monitor_recovery_state = [
            {"joint": "Joint_5", "filtered_residual_nm": 4.0, "release_limit_nm": 1.6}]
        self.fake_clock(lambda now: None)
        result = self.methods["reset_motion_interlock"](self.robot)
        self.assertIn("telemetry is stale", result["error"])
        self.assertNotIn("Joint_5", result["error"])

    def test_duplicate_reset_during_recovery_does_not_clear_hold(self):
        self.prepare_reset()

        def on_sleep(now):
            self.assertTrue(self.robot._collision_recovery_hold)
            duplicate = self.methods["reset_motion_interlock"](self.robot)
            self.assertFalse(duplicate["success"])
            self.assertTrue(duplicate["in_progress"])
            self.assertTrue(self.robot._collision_recovery_hold)
            self.robot._collision_monitor_ready = True
            self.robot._collision_monitor_state_ts = now
            self.robot._collision_monitor_acknowledgements = 1

        self.fake_clock(on_sleep)
        result = self.methods["reset_motion_interlock"](self.robot)
        self.assertTrue(result["success"])
        self.robot._collision_acknowledged_pub.publish.assert_called_once()
        self.robot.runtime_adapter.set_drive_operation_enabled.assert_called_once()

    def test_stale_ready_from_previous_acknowledgement_cannot_release_hold(self):
        self.prepare_reset()

        def on_sleep(now):
            self.assertTrue(self.robot._collision_recovery_hold)
            self.robot._collision_monitor_ready = True
            self.robot._collision_monitor_state_ts = now
            self.robot._collision_monitor_acknowledgements = 0

        self.fake_clock(on_sleep)
        result = self.methods["reset_motion_interlock"](self.robot)
        self.assertFalse(result["success"])
        self.assertTrue(self.robot._motion_interlock_active)
        self.assertIsNotNone(self.robot.last_collision_event)

    def test_matching_acknowledgement_without_readiness_times_out_held(self):
        self.prepare_reset()

        def on_sleep(now):
            self.robot._collision_monitor_ready = False
            self.robot._collision_monitor_state_ts = now
            self.robot._collision_monitor_acknowledgements = 1

        self.fake_clock(on_sleep)
        result = self.methods["reset_motion_interlock"](self.robot)
        self.assertFalse(result["success"])
        self.assertTrue(self.robot._motion_interlock_active)

    def test_new_collision_during_rearm_is_not_cleared_or_overwritten(self):
        self.prepare_reset()

        def on_sleep(now):
            self.robot._motion_interlock_active = True
            self.robot._motion_interlock_reason = "new collision"
            self.robot._collision_recovery_hold = False
            self.robot.last_collision_event = {"diagnostic_event_id": 8}
            self.robot._collision_monitor_ready = True
            self.robot._collision_monitor_state_ts = now
            self.robot._collision_monitor_acknowledgements = 1

        self.fake_clock(on_sleep)
        result = self.methods["reset_motion_interlock"](self.robot)
        self.assertFalse(result["success"])
        self.assertEqual(self.robot.last_collision_event["diagnostic_event_id"], 8)
        self.assertEqual(self.robot._motion_interlock_reason, "new collision")

    def test_drive_enable_exception_keeps_interlock_active(self):
        self.prepare_reset()
        self.robot.runtime_adapter.set_drive_operation_enabled.side_effect = RuntimeError("drive unavailable")
        result = self.methods["reset_motion_interlock"](self.robot)
        self.assertFalse(result["success"])
        self.assertTrue(self.robot._motion_interlock_active)

    def test_missing_acknowledgement_telemetry_fails_closed(self):
        self.prepare_reset()
        self.robot._collision_monitor_acknowledgements = None
        result = self.methods["reset_motion_interlock"](self.robot)
        self.assertFalse(result["success"])
        self.assertTrue(self.robot._motion_interlock_active)
        self.robot.runtime_adapter.set_drive_operation_enabled.assert_not_called()

    def test_interlock_status_distinguishes_real_and_fake_observer_requirement(self):
        self.robot._motion_interlock_reason = ""
        self.robot._collision_monitor_ready = False
        for fake in (False, True):
            with self.subTest(fake=fake):
                self.robot._fake_hardware = fake
                result = self.methods["get_motion_interlock_status"](self.robot)
                self.assertFalse(result["active"])
                self.assertFalse(result["collision_monitor_ready"])
                self.assertEqual(not fake, result["collision_monitor_required"])

    def test_motion_requires_fresh_ready_monitor_on_real_hardware(self):
        self.robot._fake_hardware = False
        self.robot._ethercat_fault_lock = threading.Lock()
        self.robot._ethercat_motion_fault = False
        callback = self.methods["is_hardware_ready_for_motion"]
        self.robot._collision_monitor_ready = False
        self.assertFalse(callback(self.robot))
        self.robot._collision_monitor_ready = True
        self.robot._collision_monitor_state_ts = time.monotonic()
        self.assertTrue(callback(self.robot))
        self.robot._collision_monitor_state_ts = time.monotonic() - 1.0
        self.assertFalse(callback(self.robot))
        self.robot._fake_hardware = True
        self.assertTrue(callback(self.robot))

    def test_readiness_callback_tracks_matching_acknowledgements_and_baseline(self):
        sample = SimpleNamespace(interface_values=[SimpleNamespace(
            interface_names=["observer_ready", "baseline_valid", "acknowledgement_count"],
            values=[1.0, 1.0, 3.0],
        ) for _ in range(6)])
        self.methods["_collision_monitor_state_callback"](self.robot, sample)
        self.assertEqual(self.robot._collision_monitor_acknowledgements, 3)
        self.assertTrue(self.robot._collision_monitor_baseline_valid)

    def test_explicit_reset_rearms_unready_observer_without_latched_collision(self):
        for stale_only in (False, True):
            with self.subTest(stale_only=stale_only):
                self.setUp()
                self.prepare_reset()
                self.robot._motion_interlock_active = False
                self.robot._motion_interlock_reason = ""
                self.robot.last_collision_event = None
                self.robot._fake_hardware = False
                self.robot._collision_monitor_ready = stale_only
                self.robot._collision_monitor_state_ts = -1.0

                def on_sleep(now):
                    self.assertTrue(self.robot._collision_recovery_hold)
                    self.robot._collision_monitor_ready = True
                    self.robot._collision_monitor_state_ts = now
                    self.robot._collision_monitor_acknowledgements = 1

                self.fake_clock(on_sleep)
                result = self.methods["reset_motion_interlock"](self.robot)
                self.assertTrue(result["success"], result)
                self.assertTrue(result["reset"])
                self.assertEqual("Collision monitor rearmed", result["message"])
                self.robot._collision_acknowledged_pub.publish.assert_called_once()
                self.assertFalse(self.robot._motion_interlock_active)
                self.assertFalse(self.robot._collision_recovery_hold)

    def test_unready_observer_reset_stays_blocked_without_confirmed_ready_ack(self):
        self.prepare_reset()
        self.robot._motion_interlock_active = False
        self.robot._motion_interlock_reason = ""
        self.robot.last_collision_event = None
        self.robot._fake_hardware = False
        self.robot._collision_monitor_ready = False
        self.fake_clock(lambda now: None)
        result = self.methods["reset_motion_interlock"](self.robot)
        self.assertFalse(result["success"])
        self.assertTrue(self.robot._motion_interlock_active)
        self.robot._collision_acknowledged_pub.publish.assert_called_once()

    def test_idle_ready_monitor_reset_remains_a_noop(self):
        self.prepare_reset()
        self.robot._motion_interlock_active = False
        self.robot._motion_interlock_reason = ""
        self.robot.last_collision_event = None
        self.robot._fake_hardware = False
        self.robot._collision_monitor_ready = True
        self.fake_clock(lambda now: None)
        self.robot._collision_monitor_state_ts = 0.0
        result = self.methods["reset_motion_interlock"](self.robot)
        self.assertTrue(result["success"])
        self.assertFalse(result["reset"])
        self.robot._collision_acknowledged_pub.publish.assert_not_called()
        self.robot.runtime_adapter.set_drive_operation_enabled.assert_not_called()

    def test_unready_observer_reset_retains_unsafe_state_check(self):
        self.prepare_reset()
        self.robot._motion_interlock_active = False
        self.robot.last_collision_event = None
        self.robot._collision_monitor_ready = False
        self.robot._interlock_reset_unsafe_reason = lambda: "robot joints are still moving"
        result = self.methods["reset_motion_interlock"](self.robot)
        self.assertFalse(result["success"])
        self.robot._collision_acknowledged_pub.publish.assert_not_called()
        self.robot.runtime_adapter.set_drive_operation_enabled.assert_not_called()

    def test_explicit_recalibration_uses_same_hold_and_sends_distinct_request(self):
        self.prepare_reset()
        self.robot._motion_interlock_active = False
        self.robot.last_collision_event = None

        def on_sleep(now):
            self.assertTrue(self.robot._collision_recovery_hold)
            self.robot._collision_monitor_ready = True
            self.robot._collision_monitor_state_ts = now
            self.robot._collision_monitor_acknowledgements = 1

        self.fake_clock(on_sleep)
        result = self.methods["reset_motion_interlock"](self.robot, recalibrate=True)
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Collision monitor recalibrated")
        request = self.robot._collision_acknowledged_pub.publish.call_args.args[0]
        self.assertTrue(json.loads(request.data)["recalibrate"])

    def test_ordinary_acknowledgement_retains_valid_baseline(self):
        self.prepare_reset()

        def on_sleep(now):
            self.robot._collision_monitor_ready = True
            self.robot._collision_monitor_state_ts = now
            self.robot._collision_monitor_acknowledgements = 1

        self.fake_clock(on_sleep)
        self.assertTrue(self.methods["reset_motion_interlock"](self.robot)["success"])
        request = self.robot._collision_acknowledged_pub.publish.call_args.args[0]
        self.assertFalse(json.loads(request.data)["recalibrate"])
        entries = [json.loads(call.args[0].split('] ', 1)[1])
                   for call in self.logger.warning.call_args_list
                   if call.args[0].startswith('[CollisionRecoveryDiagnostics]')]
        completed = next(entry for entry in entries if entry["phase"] == "reset_completed")
        self.assertTrue(completed["baseline_retained"])

    def test_invalid_baseline_or_revert_setting_requires_full_calibration(self):
        for baseline_valid, force_calibration in ((False, False), (True, True)):
            with self.subTest(baseline_valid=baseline_valid, force_calibration=force_calibration):
                self.prepare_reset()
                self.robot._collision_monitor_baseline_valid = baseline_valid
                self.methods["config"].COLLISION_RESET_RECALIBRATE_ON_RELEASE = force_calibration
                def on_sleep(now):
                    self.robot._collision_monitor_ready = True
                    self.robot._collision_monitor_state_ts = now
                    self.robot._collision_monitor_acknowledgements += 1
                self.fake_clock(on_sleep)
                self.assertTrue(self.methods["reset_motion_interlock"](self.robot)["success"])
                request = self.robot._collision_acknowledged_pub.publish.call_args.args[0]
                self.assertTrue(json.loads(request.data)["recalibrate"])


if __name__ == "__main__":
    unittest.main()
