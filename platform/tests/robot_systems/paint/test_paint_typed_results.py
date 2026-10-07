"""Error categories survive operation boundaries and cleanup remains reliable."""
import unittest
import tempfile
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import numpy as np

from src.engine.vision.i_capture_snapshot_service import VisionCaptureSnapshot
from src.robot_systems.paint.processes.paint.config import PaintProcessConfig
from src.robot_systems.paint.processes.paint.execute.pickup_executor import PaintPickupExecutor
from src.robot_systems.paint.processes.paint.execution_control import PaintExecutionControl
from src.robot_systems.paint.processes.paint.execution_machine.context import PaintExecutionContext
from src.robot_systems.paint.processes.paint.execution_machine.machine_factory import PaintExecutionMachineFactory
from src.robot_systems.paint.processes.paint.execution_machine.state import PaintExecutionState
from src.robot_systems.paint.processes.paint.execution_machine.handlers.common.motion_handlers import finish_paint_motion
from src.robot_systems.paint.processes.paint.execution_machine.handlers.lifecycle.terminal_common import restore_cycle_resources
from src.robot_systems.paint.processes.paint.execution_machine.handlers.workflow.preparation_handler import handle_prepare_workpiece
from src.robot_systems.paint.processes.paint.execution_machine.handlers.dropoff.dropoff_handlers import _execute_plate_layout_ordered_release
from src.robot_systems.paint.processes.paint.match.workpiece_matching_service import PaintWorkpieceMatchingService
from src.robot_systems.paint.processes.paint.match.results import NoMatch
from src.robot_systems.paint.processes.paint.plan.workpiece_preparation_service import PaintWorkpiecePreparationService
from src.robot_systems.paint.processes.paint.plan.pickup_transfer_planner import PaintPickupTransferPlanner
from src.robot_systems.paint.processes.paint.results import (
    Failed, Ready, PaintFailureCode, PaintOperationError, PaintOperationResult, PaintOutcome,
)
from src.robot_systems.paint.processes.paint.incremental_adjustment import (
    AdjustmentPhase, AdjustmentStep, PaintAdjustmentSession, NextPaintSection,
    FinishAdjustment, CancelAdjustment,
)
from src.robot_systems.paint.processes.paint.paint_process import PaintProcess
from src.shared_contracts.events.process_events import ProcessState
from src.robot_systems.paint.domain.workpieces.repository.json_paint_workpiece_repository import JsonPaintWorkpieceRepository
from src.robot_systems.paint.domain.workpieces.service.paint_workpiece_service import PaintWorkpieceService
from src.robot_systems.paint.domain.workpieces.errors import WorkpieceReadError
from tests.robot_systems.paint.test_tray_readiness import tray_config, reserve
from src.robot_systems.paint.processes.paint.tray_dry.plate_layout import PlateLayoutService


def contour():
    return np.asarray([[[0, 0]], [[10, 0]], [[10, 10]], [[0, 10]]], dtype=np.float32)


def context(service=None):
    service = service or MagicMock()
    service._path_executor._plate_layout_service = None
    return PaintExecutionContext(service, lambda: False, PaintExecutionControl(),
                                 process_config=PaintProcessConfig())


class TestPaintTypedResults(unittest.TestCase):
    def test_corrupt_saved_record_is_storage_failure_through_real_service(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = JsonPaintWorkpieceRepository(directory)
            folder = Path(directory) / "2026-10-07" / "saved"
            folder.mkdir(parents=True)
            (folder / "saved_workpiece.json").write_text("{broken JSON", encoding="utf-8")
            workpieces = PaintWorkpieceService(repository)
            matcher = PaintWorkpieceMatchingService(
                list_saved_workpieces_fn=workpieces.list_for_matching,
                load_saved_workpiece_fn=workpieces.load_for_matching,
                run_matching_fn=MagicMock(),
            )
            with self.assertLogs(level="ERROR"):
                result = matcher.match_result(contour())
            self.assertIs(result.failure.code, PaintFailureCode.STORAGE)
            self.assertIn("saved", result.failure.message)
            with self.assertLogs(level="WARNING"):
                self.assertEqual(repository.list_all(), [])
            with self.assertRaises(WorkpieceReadError) as raised:
                workpieces.load_for_matching("saved")
            self.assertIsNotNone(raised.exception.__cause__)
            self.assertIsNone(workpieces.load_for_matching("missing"))

    def test_unreadable_library_root_is_not_empty_match_through_service(self):
        repository = MagicMock()
        repository.list_for_matching.side_effect = OSError("library unavailable")
        workpieces = PaintWorkpieceService(repository)
        matcher = PaintWorkpieceMatchingService(
            list_saved_workpieces_fn=workpieces.list_for_matching,
            load_saved_workpiece_fn=workpieces.load_for_matching,
            run_matching_fn=MagicMock(),
        )
        with self.assertLogs(level="ERROR"):
            result = matcher.match_result(contour())
        self.assertIs(result.failure.code, PaintFailureCode.STORAGE)

    def test_adjustment_cancel_does_not_require_a_second_stop_poll(self):
        session = PaintAdjustmentSession()
        stopped = MagicMock(side_effect=[True, False])
        self.assertIsInstance(session.wait_for_command_result(stopped), CancelAdjustment)
        stopped.assert_called_once()

    def test_adjustment_commands_distinguish_next_finish_and_cancel(self):
        session = PaintAdjustmentSession()
        session.inspection_ready(10, 100, complete=False)
        self.assertIs(session.snapshot().phase, AdjustmentPhase.INSPECT)
        step = AdjustmentStep(10, 20, 0)
        self.assertTrue(session.request_next(step))
        command = session.wait_for_command_result(lambda: False)
        self.assertIsInstance(command, NextPaintSection)
        self.assertIs(command.step, step)
        session.inspection_ready(20, 100, complete=False)
        self.assertTrue(session.request_finish())
        self.assertIsInstance(session.wait_for_command_result(lambda: False), FinishAdjustment)
        self.assertIsInstance(session.wait_for_command_result(lambda: True), CancelAdjustment)
        with self.assertRaises(TypeError):
            NextPaintSection(None)

    def test_process_exposes_actionable_failure_from_typed_production_result(self):
        production = MagicMock()
        result = PaintOperationResult.failed(PaintFailureCode.STORAGE, "matching", "storage unavailable")
        production.run_once_result.return_value = result
        process = PaintProcess(production, MagicMock())
        process.start()
        process._thread.join(timeout=2)
        self.assertFalse(process._thread.is_alive())
        self.assertIs(process.state, ProcessState.ERROR)
        self.assertIs(process.last_failure, result.failure)

    def test_failed_result_requires_failure_and_success_cannot_carry_one(self):
        with self.assertRaises(ValueError):
            PaintOperationResult(PaintOutcome.FAILED, "bad")
        failure = PaintOperationResult.failed(PaintFailureCode.MOTION, "pickup", "rejected").failure
        with self.assertRaises(ValueError):
            PaintOperationResult(PaintOutcome.COMPLETED, "done", failure)
        with self.assertRaises(ValueError):
            PaintOperationResult(PaintOutcome.FAILED, "bad", failure,
                                 stop_reason=PaintOutcome.TRAY_FULL)

    def test_context_boolean_and_message_are_views_of_one_result(self):
        ctx = context()
        failed = PaintOperationResult.failed(PaintFailureCode.STORAGE, "match", "unavailable")
        ctx.set_outcome(failed)
        self.assertIs(ctx.result, failed)
        self.assertIs(ctx.operation_failure, failed.failure)
        self.assertFalse(ctx.result_ok)
        ctx.set_result(True, "done")
        self.assertTrue(ctx.result_ok)
        self.assertIsNone(ctx.operation_failure)

    def test_planning_empty_jobs_reports_explicit_reason_without_motion(self):
        owner = MagicMock()
        planner = PaintPickupTransferPlanner(owner)
        with self.assertRaises(PaintOperationError) as raised:
            planner.build_required_plan(SimpleNamespace(execution_jobs=[]))
        self.assertIs(raised.exception.failure.code, PaintFailureCode.PLANNING)
        self.assertIn("execution job", str(raised.exception))
        owner._robot_service.execute_ordered_motion_chain.assert_not_called()

    def test_pickup_invalid_mode_is_rejected_before_vacuum_or_motion(self):
        owner = MagicMock()
        owner._active_execution_control = None
        result = PaintPickupExecutor(owner).execute_result(
            object(), pickup_plan=SimpleNamespace(contact_mode="invalid"))
        self.assertIs(result.failure.code, PaintFailureCode.INVALID_CONFIGURATION)
        owner._motion.turn_vacuum_on.assert_not_called()
        owner._motion.move_ordered_pickup_sequence.assert_not_called()

    def test_height_measure_is_unavailable_rather_than_invalid_mode(self):
        owner = MagicMock()
        result = PaintPickupExecutor(owner).execute_result(
            object(), pickup_plan=SimpleNamespace(contact_mode="height_measure"))
        self.assertIs(result.failure.code, PaintFailureCode.UNAVAILABLE)
        owner._motion.turn_vacuum_on.assert_not_called()

    def test_pickup_vacuum_failure_preserves_its_message_and_category(self):
        owner = MagicMock()
        owner._active_execution_control = None
        owner._motion.turn_vacuum_on.return_value = False, "vacuum controller disconnected"
        plan = SimpleNamespace(contact_mode="planned", waypoints=(object(), object()),
                               contact_waypoint_index=1, motion_plan=object(),
                               change_plane_combined_with_first_contact=False,
                               vacuum_on_before_moves=True)
        result = PaintPickupExecutor(owner).execute_result(object(), pickup_plan=plan)
        self.assertIs(result.failure.code, PaintFailureCode.VACUUM)
        self.assertEqual(result.message, "vacuum controller disconnected")
        owner._motion.move_ordered_pickup_sequence.assert_not_called()

    def test_pickup_cancellation_is_not_a_motion_failure(self):
        owner = MagicMock()
        owner._active_execution_control.should_stop.return_value = True
        plan = SimpleNamespace(contact_mode="planned", waypoints=(object(), object()),
                               contact_waypoint_index=1)
        result = PaintPickupExecutor(owner).execute_result(object(), pickup_plan=plan)
        self.assertIs(result.outcome, PaintOutcome.CANCELLED)
        self.assertIsNone(result.failure)
        owner._motion.turn_vacuum_on.assert_not_called()

    def matcher(self, list_fn):
        return PaintWorkpieceMatchingService(list_saved_workpieces_fn=list_fn,
                                            load_saved_workpiece_fn=MagicMock(),
                                            run_matching_fn=MagicMock())

    def test_empty_repository_and_storage_failure_are_distinct(self):
        absent = self.matcher(lambda: []).match_result(contour())
        self.assertIsInstance(absent, NoMatch)
        with self.assertLogs(level="ERROR"):
            failed = self.matcher(MagicMock(side_effect=OSError("storage unavailable"))).match_result(contour())
        self.assertIsInstance(failed, Failed)
        self.assertIs(failed.failure.code, PaintFailureCode.STORAGE)

    def test_matcher_bug_is_internal_with_traceback(self):
        with self.assertLogs(level="ERROR") as logs:
            result = self.matcher(MagicMock(side_effect=AttributeError("broken repository adapter"))).match_result(contour())
        self.assertIs(result.failure.code, PaintFailureCode.INTERNAL)
        self.assertIn("AttributeError", logs.output[0])

    def test_storage_failure_survives_preparation_and_dashboard_boundary(self):
        matcher = self.matcher(MagicMock(side_effect=OSError("storage unavailable")))
        preparation = PaintWorkpiecePreparationService(
            can_match_fn=matcher.can_match_saved_workpieces,
            match_workpiece_fn=matcher.match_saved_workpieces,
            typed_match_workpiece_fn=matcher.match_result,
        )
        service = MagicMock()
        service._workpiece_preparation = preparation
        ctx = context(service)
        ctx.snapshot = VisionCaptureSnapshot(frame=None, contours=[contour()], source="test")
        with self.assertLogs(level="ERROR"):
            state = handle_prepare_workpiece(ctx)
        self.assertIs(state, PaintExecutionState.ERROR)
        self.assertIs(ctx.result.failure.code, PaintFailureCode.STORAGE)
        self.assertEqual(ctx.result_message, "storage unavailable")
        service.publish_dashboard_message.assert_called_once_with(
            "error", "Workpiece preparation failed", "storage unavailable")

    def test_live_settings_failure_does_not_fall_back_to_stale_defaults(self):
        service = PaintWorkpiecePreparationService(
            can_match_fn=lambda: False, match_workpiece_fn=MagicMock(),
            default_settings={"velocity": 99},
            default_settings_getter=MagicMock(side_effect=OSError("settings unavailable")),
        )
        with self.assertLogs(level="ERROR"):
            result = service.prepare_result(contour(), None)
        self.assertIsInstance(result, Failed)
        self.assertIs(result.failure.code, PaintFailureCode.STORAGE)

    def test_timing_disk_failure_cannot_prevent_motion_cleanup(self):
        ctx = context()
        ctx.paint_motion_active = True
        ctx.paint_previous_control = object()
        ctx.paint_timing_session = MagicMock()
        ctx.paint_timing_recorder = MagicMock()
        ctx.paint_timing_recorder.write_csv.side_effect = OSError("disk full")
        ctx.production_service._path_executor._diagnostics_artifacts_enabled.return_value = True
        with self.assertLogs(level="WARNING"):
            finish_paint_motion(ctx, success=False)
        self.assertFalse(ctx.paint_motion_active)
        self.assertIs(ctx.production_service._path_executor._active_execution_control,
                      ctx.paint_previous_control)
        ctx.paint_timing_session.__exit__.assert_called_once()

    def test_cleanup_attempts_other_resources_and_preserves_primary_failure(self):
        ctx = context()
        ctx.set_outcome(PaintOperationResult.failed(PaintFailureCode.MOTION, "pickup", "robot rejected"))
        service = ctx.production_service
        service._path_executor._plate_layout_service = MagicMock()
        service._restore_brightness.side_effect = OSError("brightness disconnected")
        with self.assertRaises(PaintOperationError) as raised:
            restore_cycle_resources(ctx)
        self.assertIs(raised.exception.failure.code, PaintFailureCode.MOTION)
        self.assertEqual(raised.exception.failure.secondary_failures[0].stage, "cycle_cleanup")
        self.assertIsInstance(raised.exception.__cause__, OSError)
        service._path_executor._plate_layout_service.cancel.assert_called_once()
        service._set_dashboard_live_view_paused.assert_called_once()

    def test_unexpected_handler_failure_runs_terminal_cleanup(self):
        ctx = context()
        ctx.paint_motion_active = True
        ctx.paint_previous_control = object()
        ctx.paint_timing_session = MagicMock()
        ctx.production_service._path_executor._plate_layout_service = MagicMock()
        with patch("src.robot_systems.paint.processes.paint.execution_machine.machine_factory.handle_capture_workpiece",
                   side_effect=RuntimeError("camera backend bug")):
            machine = PaintExecutionMachineFactory().build(ctx, initial_state=PaintExecutionState.CAPTURE_WORKPIECE)
            with self.assertLogs(level="ERROR"):
                machine.start_execution()
        self.assertIs(ctx.result.failure.code, PaintFailureCode.INTERNAL)
        self.assertEqual(ctx.result.failure.stage, "capture_workpiece")
        self.assertFalse(ctx.paint_motion_active)
        self.assertIs(machine.current_state, PaintExecutionState.IDLE)
        ctx.production_service._path_executor._plate_layout_service.cancel.assert_called_once()

    def test_missing_exit_profile_is_rejected_before_entry_or_release(self):
        layout = PlateLayoutService()
        layout.clear()
        config = tray_config()
        config = replace(config, dropoff=replace(config.dropoff,
            plate_exit_gate_pose=[0, 0, 100, 180, 0, 0], plate_use_center_waypoint=False,
            plate_motion_profiles=[profile for profile in config.dropoff.plate_motion_profiles
                                   if profile["key"] != "exit_gate"]))
        reserve(layout, config)
        executor = MagicMock()
        executor._plate_layout_service = layout
        executor._paint_process_config.return_value = config
        executor._contact_motion_config.rotation_index = 5
        executor._last_process_end_pose = [0, 0, 100, 180, 0, 0]
        with self.assertRaises(ValueError):
            _execute_plate_layout_ordered_release(executor, next_cycle_start=None)
        executor._motion.move_ordered_pickup_sequence.assert_not_called()
        executor._motion.turn_vacuum_off.assert_not_called()
        self.assertIsNotNone(layout.pending)
        self.assertEqual(layout.snapshot(config.dropoff)["placements"], [])
