"""Callers can branch on stable error codes, including failures raised by hardware."""
import unittest
from dataclasses import FrozenInstanceError
from threading import Event
from types import SimpleNamespace
from unittest.mock import MagicMock

from src.engine.robot.interfaces.i_tool_service import IToolService
from src.engine.robot.interfaces.tool_definition import ToolDefinition
from src.engine.robot.interfaces.tool_operation_result import (
    ToolErrorCode, ToolErrorInfo, ToolOperationFailure, ToolOperationResult,
)
from src.engine.robot.tool_changer import SlotConfig, ToolChangeStep, ToolChanger
from src.engine.robot.tool_manager import ToolManager


class ToolOperationResultTests(unittest.TestCase):
    def test_success_supports_typed_fields_and_legacy_unpacking(self):
        result = ToolOperationResult(message="Done")
        self.assertTrue(result.success)
        self.assertTrue(result)
        self.assertIsNone(result.error)
        self.assertEqual(result.as_tuple(), (True, "Done"))
        ok, message = result
        self.assertTrue(ok)
        self.assertEqual(message, "Done")
        self.assertTrue(result[0])
        self.assertEqual(result[1], "Done")

    def test_failure_is_immutable_and_preserves_structured_error(self):
        result = ToolOperationResult.failure(ToolErrorCode.MOTION_FAILED, "Failed", step_number=2,
                                             detail="Transport timeout")
        self.assertFalse(result)
        self.assertFalse(result.success)
        self.assertIsInstance(result.error, ToolErrorInfo)
        self.assertEqual(result.error.code, ToolErrorCode.MOTION_FAILED)
        self.assertEqual(result.error.step_number, 2)
        self.assertEqual(result.error.detail, "Transport timeout")
        self.assertEqual(tuple(result), (False, "Failed"))
        with self.assertRaises(FrozenInstanceError):
            result.message = "Changed"
        with self.assertRaises(FrozenInstanceError):
            result.error.code = ToolErrorCode.CANCELLED

    def test_error_message_is_authoritative(self):
        result = ToolOperationResult(message="Success", error=ToolErrorInfo(ToolErrorCode.BUSY, "Busy"))
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Busy")

    def test_interface_defaults_return_typed_unsupported_failures(self):
        service = MagicMock(spec=IToolService)
        result = IToolService.execute_sequence(service, 2, [])
        self.assertIsInstance(result, ToolOperationResult)
        self.assertEqual(result.error.code, ToolErrorCode.UNSUPPORTED)
        result = IToolService.pickup_tool(service, 7, cancelled=Event())
        self.assertEqual(result.error.code, ToolErrorCode.UNSUPPORTED)
        service.pickup_gripper.assert_not_called()


class ToolManagerTypedFailureTests(unittest.TestCase):
    def setUp(self):
        self.motion = MagicMock()
        self.motion.move_linear.return_value = True
        self.robot = MagicMock()
        self.robot.is_healthy.return_value = True
        self.robot.get_state.return_value = "idle"
        self.robot.get_current_velocity.return_value = 0.0
        self.robot.set_active_tool.return_value = True
        self.slot = SlotConfig(2, 7, pickup_sequence=[ToolChangeStep(pose=[0] * 6)],
                               dropoff_sequence=[ToolChangeStep(kind="detach")])
        self.config = SimpleNamespace(robot_tool=0, robot_user=0)
        self.manager = ToolManager(self.motion, ToolChanger([self.slot], [ToolDefinition(7, "Tool")]),
                                   self.config, SimpleNamespace(movement_groups={}), tool_activator=self.robot)

    def test_busy_and_recovery_failures_have_distinct_codes(self):
        with self.manager._lock:
            self.assertEqual(self.manager.pickup_tool(7).error.code, ToolErrorCode.BUSY)
        self.motion.move_linear.return_value = False
        self.assertEqual(self.manager.pickup_tool(7).error.code, ToolErrorCode.MOTION_FAILED)
        self.assertEqual(self.manager.pickup_tool(7).error.code, ToolErrorCode.RECOVERY_REQUIRED)

    def test_unknown_tool_and_missing_slot_have_distinct_codes(self):
        self.assertEqual(self.manager.pickup_tool(99).error.code, ToolErrorCode.TOOL_NOT_FOUND)
        self.slot.tool_id = None
        self.assertEqual(self.manager.pickup_tool(7).error.code, ToolErrorCode.SLOT_NOT_FOUND)
        self.motion.move_linear.assert_not_called()

    def test_motion_exception_retains_code_message_and_step_number(self):
        self.slot.pickup_sequence.insert(0, ToolChangeStep(kind="wait", wait_seconds=0))
        self.motion.move_linear.side_effect = TimeoutError("Request-sent")
        result = self.manager.pickup_tool(7)
        self.assertEqual(result.error.code, ToolErrorCode.MOTION_FAILED)
        self.assertEqual(result.error.step_number, 2)
        self.assertEqual(result.message, "Request-sent")
        self.assertEqual(result.error.detail, "TimeoutError")
        self.assertTrue(self.manager.recovery_required)
        self.assertEqual(self.motion.move_linear.call_count, 1)

    def test_activation_failure_and_exception_are_classified(self):
        self.slot.pickup_sequence = [ToolChangeStep(kind="attach")]
        self.robot.set_active_tool.return_value = False
        result = self.manager.pickup_tool(7)
        self.assertEqual(result.error.code, ToolErrorCode.ACTIVATION_FAILED)
        self.assertEqual(result.error.step_number, 1)
        self.assertEqual(self.config.robot_tool, 0)
        self.manager._recovery_required = False
        self.robot.set_active_tool.side_effect = OSError("Disconnected")
        result = self.manager.pickup_tool(7)
        self.assertEqual(result.error.code, ToolErrorCode.ACTIVATION_FAILED)
        self.assertEqual(result.error.detail, "OSError")

    def test_cancellation_remains_distinct_from_motion_failure(self):
        cancelled = Event()
        cancelled.set()
        result = self.manager.pickup_tool(7, cancelled=cancelled)
        self.assertEqual(result.error.code, ToolErrorCode.CANCELLED)
        self.assertFalse(self.manager.recovery_required)
        self.motion.move_linear.assert_not_called()

    def test_bad_draft_returns_invalid_sequence_not_unexpected_error(self):
        result = self.manager.execute_sequence(2, [{"kind": "motion", "pose": [1, 2]}])
        self.assertEqual(result.error.code, ToolErrorCode.INVALID_SEQUENCE)
        self.motion.move_linear.assert_not_called()

    def test_preflight_reports_invalid_step_before_any_motion(self):
        self.slot.pickup_sequence.append(ToolChangeStep(pose=[1] * 6, velocity=0))
        result = self.manager.pickup_tool(7)
        self.assertEqual(result.error.code, ToolErrorCode.INVALID_SEQUENCE)
        self.assertEqual(result.error.step_number, 2)
        self.motion.move_linear.assert_not_called()

    def test_robot_feedback_exceptions_are_robot_unavailable(self):
        self.robot.get_state.side_effect = ConnectionError("offline")
        self.assertEqual(self.manager.pickup_tool(7).error.code, ToolErrorCode.ROBOT_UNAVAILABLE)

    def test_missing_confirmation_and_declined_confirmation_are_distinct(self):
        self.slot.pickup_sequence = [ToolChangeStep(kind="operator_confirm")]
        self.assertEqual(self.manager.pickup_tool(7).error.code, ToolErrorCode.CONFIRMATION_REQUIRED)
        self.manager._operator_confirmation = lambda _: False
        result = self.manager.pickup_tool(7)
        self.assertEqual(result.error.code, ToolErrorCode.CONFIRMATION_DECLINED)
        self.assertEqual(result.error.step_number, 1)

    def test_configuration_provider_failure_has_a_configuration_code(self):
        def unavailable():
            raise ValueError("Duplicate slots")
        self.manager._configuration_provider = unavailable
        self.assertEqual(self.manager.pickup_tool(7).error.code, ToolErrorCode.CONFIGURATION_ERROR)
        self.assertFalse(self.manager.recovery_required)

    def test_position_guard_preserves_codes_through_public_boundary(self):
        self.manager._tool_change_group = "Tool Changer"
        result = self.manager.pickup_tool(7)
        self.assertEqual(result.error.code, ToolErrorCode.POSITION_NOT_CONFIGURED)
        group = SimpleNamespace(parse_position=lambda: [0] * 6)
        self.manager._movement_groups.movement_groups["Tool Changer"] = group
        self.robot.get_current_position_fresh.side_effect = TimeoutError("no pose")
        self.assertEqual(self.manager.pickup_tool(7).error.code, ToolErrorCode.POSE_UNAVAILABLE)
        self.robot.get_current_position_fresh.side_effect = None
        self.robot.get_current_position_fresh.return_value = [20] * 6
        self.assertEqual(self.manager.pickup_tool(7).error.code, ToolErrorCode.NOT_AT_TOOL_CHANGER)
        self.motion.move_linear.assert_not_called()

    def test_validation_raises_typed_exception_for_internal_callers(self):
        with self.assertRaises(ToolOperationFailure) as caught:
            self.manager._validate_sequence([ToolChangeStep(pose=[0] * 6, velocity=0)], 7)
        self.assertEqual(caught.exception.error.code, ToolErrorCode.INVALID_SEQUENCE)
