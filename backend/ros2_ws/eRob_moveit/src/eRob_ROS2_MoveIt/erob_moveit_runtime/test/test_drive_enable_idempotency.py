"""Drive acknowledgement must preserve an existing hardware hold."""
import ast
from pathlib import Path
from threading import Lock
from types import MethodType, SimpleNamespace
import unittest
from unittest.mock import MagicMock
import numpy as np


def adapter_methods():
    path = Path(__file__).resolve().parents[1] / "scripts/backend/runtime_adapter.py"
    tree = ast.parse(path.read_text())
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef)
               and node.name == "ZeroErrRuntimeAdapter")
    methods = [node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name in {
        "set_drive_operation_enabled", "_drive_state_callback", "_decode_statusword_state"}]
    for method in methods:
        method.decorator_list = []
    namespace = {"np": np, "time": SimpleNamespace(monotonic=lambda: 100.0, sleep=MagicMock()),
                 "config": SimpleNamespace(NUM_JOINTS=6), "DynamicJointState": SimpleNamespace,
                 "Float64MultiArray": SimpleNamespace}
    exec(compile(ast.fix_missing_locations(ast.Module(body=methods, type_ignores=[])),
                 str(path), "exec"), namespace)
    return namespace


class TestDriveEnableIdempotency(unittest.TestCase):
    def setUp(self):
        self.methods = adapter_methods()
        self.adapter = SimpleNamespace(
            _drive_state_lock=Lock(), _drive_enable_lock=Lock(), _drive_state_ts=99.9,
            _drive_operation_enabled_requested=False,
            _drive_statusword=np.full(6, 0x27, dtype=float),
            _drive_error_code=np.zeros(6), _drive_mode_display=np.zeros(6),
            _drive_joint_order=[f"Joint_{i+1}" for i in range(6)],
            _ensure_drive_set_controllers_active=MagicMock(return_value=False),
            _drive_enable_set_pub=MagicMock(), _drive_disable_set_pub=MagicMock(),
        )
        self.adapter._decode_statusword_state = MethodType(
            self.methods["_decode_statusword_state"], self.adapter)
        self.robot = SimpleNamespace(
            is_hardware_ready_for_drive_enable=lambda: True,
            is_hardware_ready_for_motion=lambda: False,
            get_hardware_fault_reason=lambda: "interlocked",
            get_logger=MagicMock(), _send_hold_position_trajectory=MagicMock(),
            _runtime_dynamic_input_period=0.0,
        )

    def enable(self):
        return self.methods["set_drive_operation_enabled"](self.adapter, self.robot, True)

    def test_enabled_drives_restore_request_without_goal_or_pulse(self):
        result = self.enable()
        self.assertTrue(result["success"])
        self.assertTrue(result["already_enabled"])
        self.assertTrue(self.adapter._drive_operation_enabled_requested)
        self.adapter._ensure_drive_set_controllers_active.assert_not_called()
        self.robot._send_hold_position_trajectory.assert_not_called()
        self.adapter._drive_enable_set_pub.publish.assert_not_called()
        self.adapter._drive_disable_set_pub.publish.assert_not_called()
        self.methods["time"].sleep.assert_not_called()

    def test_stale_incomplete_disabled_and_faulted_states_require_enable_path(self):
        for field, value in [
            ("_drive_state_ts", 99.0), ("_drive_state_ts", 0.0),
            ("_drive_statusword", np.array([0x27] * 5 + [0x23])),
            ("_drive_statusword", np.array([0x27] * 5)),
            ("_drive_error_code", np.array([0] * 5 + [1])),
            ("_drive_error_code", np.array([0] * 5 + [float("nan")])),
        ]:
            with self.subTest(field=field, value=value):
                self.setUp()
                setattr(self.adapter, field, value)
                self.assertFalse(self.enable().get("success", False))
                self.adapter._ensure_drive_set_controllers_active.assert_called_once()
                self.assertFalse(self.adapter._drive_operation_enabled_requested)

    def test_disabled_drives_still_receive_hold_and_enable_pulse(self):
        self.adapter._drive_statusword.fill(0x23)
        self.adapter._ensure_drive_set_controllers_active.return_value = True
        self.adapter._deactivate_drive_set_controllers = MagicMock(return_value=True)
        result = self.enable()
        self.assertTrue(result["success"])
        self.robot._send_hold_position_trajectory.assert_called_once_with(
            reason="drive enable", suppress_drive_disable_cancel=True)
        self.assertEqual(self.adapter._drive_enable_set_pub.publish.call_count, 2)
        self.adapter._deactivate_drive_set_controllers.assert_called_once()

    def test_existing_safety_gate_still_prevents_enable(self):
        self.robot.is_hardware_ready_for_drive_enable = lambda: False
        self.assertFalse(self.enable()["success"])
        self.assertFalse(self.adapter._drive_operation_enabled_requested)
        self.adapter._ensure_drive_set_controllers_active.assert_not_called()

    def test_only_complete_drive_telemetry_can_skip_enable(self):
        sample = SimpleNamespace(
            joint_names=self.adapter._drive_joint_order,
            interface_values=[SimpleNamespace(
                interface_names=["statusword", "error_code"], values=[0x27, 0.0])
                for _ in range(6)])
        callback = self.methods["_drive_state_callback"]
        callback(self.adapter, self.robot, sample)
        self.assertEqual(self.adapter._drive_state_ts, 100.0)
        sample.interface_values[-1].interface_names = ["statusword"]
        sample.interface_values[-1].values = [0x27]
        callback(self.adapter, self.robot, sample)
        self.assertEqual(self.adapter._drive_state_ts, 0.0)


if __name__ == "__main__":
    unittest.main()
