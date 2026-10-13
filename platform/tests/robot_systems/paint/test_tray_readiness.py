"""Tray confirmation protects physical occupancy across UI and production paths."""
import unittest
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from src.robot_systems.paint.applications.dashboard.controller.paint_dashboard_controller import PaintDashboardController
from src.robot_systems.paint.applications.dashboard.dashboard_state import DashboardState
from src.robot_systems.paint.applications.dashboard.model.paint_dashboard_model import PaintDashboardModel
from src.robot_systems.paint.applications.dashboard.service.i_paint_dashboard_service import DashboardCommandResult
from src.robot_systems.paint.applications.dashboard.service.paint_dashboard_service import PaintDashboardService
from src.robot_systems.paint.processes.paint.configuration.models import PaintDropoffConfig, PaintProcessConfig
from src.robot_systems.paint.processes.paint.workflow.context import PaintExecutionContext
from src.robot_systems.paint.processes.paint.workflow.machine_factory import PaintExecutionMachineFactory
from src.robot_systems.paint.processes.paint.workflow.state import PaintExecutionState
from src.robot_systems.paint.processes.paint.production.execution_control import PaintExecutionControl
from src.robot_systems.paint.processes.paint.paint_process import PaintProcess
from src.robot_systems.paint.processes.paint.production.service import PaintProductionService
from src.robot_systems.paint.processes.paint.tray_dry.errors import (
    TrayBusyError, TrayConfirmationRequiredError, TrayErrorCode, TrayLayoutChangedError,
)
from src.robot_systems.paint.processes.paint.tray_dry.plate_layout import PlateLayoutService, TrayReadiness
from src.shared_contracts.events.process_events import ProcessState


def tray_config():
    return PaintProcessConfig(dropoff=PaintDropoffConfig(
        strategy="plate_layout",
        plate_corners=[[0, 0, 10, 180, 0, 0], [200, 0, 10, 180, 0, 0],
                       [200, 200, 10, 180, 0, 0], [0, 200, 10, 180, 0, 0]],
        plate_passage_gate_pose=[0, 0, 100, 180, 0, 0],
    ))


def reserve(layout, config):
    return layout.reserve(config.dropoff, width_mm=20, height_mm=30,
                          calibration_pose=[0, 0, 0, 180, 0, 0],
                          workpiece_rz_at_calibration_deg=0,
                          pose_calculator=lambda _calibration, target, _rz: list(target))


class TestTrayReadiness(unittest.TestCase):
    def setUp(self):
        self.layout = PlateLayoutService()
        self.config = tray_config()
        self.settings = MagicMock()
        self.settings.get_snapshot.return_value = self.config
        self.process = MagicMock(state=ProcessState.STOPPED)
        self.process.is_stopping = False
        self.service = PaintDashboardService(self.process,
            plate_layout_service=self.layout, paint_process_config_service=self.settings)

    def test_restart_requires_confirmation_and_does_not_start(self):
        self.assertIs(self.layout.readiness, TrayReadiness.UNKNOWN)
        with self.assertRaises(TrayConfirmationRequiredError) as caught:
            self.service.start()
        self.assertIs(caught.exception.as_failure().code, TrayErrorCode.CONFIRMATION_REQUIRED)
        self.process.start.assert_not_called()
        self.assertTrue(self.service.confirm_empty_tray().success)
        self.service.start()
        self.service.start()
        self.assertEqual(self.process.start.call_count, 2)
        self.assertIs(PlateLayoutService().readiness, TrayReadiness.UNKNOWN)

    def test_confirmation_rejected_while_running_paused_or_stopping(self):
        for state, stopping in [(ProcessState.RUNNING, False), (ProcessState.PAUSED, False),
                                (ProcessState.STOPPED, True)]:
            with self.subTest(state=state, stopping=stopping):
                self.process.state = state
                self.process.is_stopping = stopping
                result = self.service.confirm_empty_tray()
                self.assertFalse(result.success)
                self.assertIs(result.failure.code, TrayErrorCode.BUSY)
                self.assertIs(self.layout.readiness, TrayReadiness.UNKNOWN)

    def test_unavailable_tray_has_typed_failure(self):
        result = PaintDashboardService(self.process).confirm_empty_tray()
        self.assertFalse(result.success)
        self.assertIs(result.failure.code, TrayErrorCode.UNAVAILABLE)

    def test_active_reservation_cannot_be_cleared(self):
        self.layout.clear()
        reservation, error = reserve(self.layout, self.config)
        self.assertEqual(error, "")
        result = self.service.confirm_empty_tray()
        self.assertIs(result.failure.code, TrayErrorCode.BUSY)
        self.assertIs(self.layout.pending, reservation)

    def test_settings_change_preserves_occupancy_and_requires_explicit_reset(self):
        self.layout.clear()
        first, error = reserve(self.layout, self.config)
        self.assertEqual(error, "")
        self.layout.commit(self.config.dropoff)
        changed = replace(self.config, dropoff=replace(self.config.dropoff, plate_spacing_x_mm=25))
        with self.assertRaises(TrayLayoutChangedError):
            reserve(self.layout, changed)
        placements = self.layout.snapshot(changed.dropoff)["placements"]
        self.assertEqual(len(placements), 1)
        self.assertEqual(placements[0]["placement_id"], first.placement_id)
        self.settings.get_snapshot.return_value = changed
        with self.assertRaises(TrayLayoutChangedError):
            self.service.start()
        self.assertTrue(self.service.confirm_empty_tray().success)
        second, error = reserve(self.layout, changed)
        self.assertEqual(error, "")
        self.assertIsNotNone(second)

    def test_reservation_cannot_implicitly_confirm_an_unknown_tray(self):
        with self.assertRaises(TrayConfirmationRequiredError):
            reserve(self.layout, self.config)
        self.assertIsNone(self.layout.pending)

    def test_automatic_destination_does_not_require_tray_confirmation(self):
        self.settings.get_snapshot.return_value = PaintProcessConfig()
        self.service.start()
        self.process.start.assert_called_once()
        self.assertIs(self.layout.readiness, TrayReadiness.UNKNOWN)

    def test_success_cannot_contain_failure(self):
        with self.assertRaises(ValueError):
            DashboardCommandResult(True, "", failure=TrayBusyError().as_failure())

    def production(self):
        return PaintProductionService(workpiece_preparation_service=MagicMock(),
            capture_snapshot_service=MagicMock(), path_preparation_service=MagicMock(),
            path_executor=MagicMock(), paint_process_config_service=self.settings,
            plate_layout_service=self.layout)

    def test_direct_production_is_blocked_before_capture_or_motion(self):
        production = self.production()
        with self.assertRaises(TrayConfirmationRequiredError):
            production.run_once()
        self.assertEqual(production._capture_snapshot_service.mock_calls, [])
        self.assertEqual(production._path_executor.mock_calls, [])

    def test_direct_process_start_is_blocked_and_retains_typed_failure(self):
        production = self.production()
        process = PaintProcess(production, MagicMock())
        with self.assertRaises(TrayConfirmationRequiredError):
            process.start()
        self.assertIs(process.state, ProcessState.IDLE)
        self.assertIsNone(process._thread)
        self.assertIs(process.last_failure.code, TrayErrorCode.CONFIRMATION_REQUIRED)

    def test_demo_checks_tray_before_automatic_first_cycle(self):
        self.settings.get_snapshot.return_value = replace(self.config,
            dropoff=replace(self.config.dropoff, strategy="movement_group", alternate_drying_demo=True))
        with self.assertRaises(TrayConfirmationRequiredError):
            self.production().run_once()

    def test_state_handler_preserves_failure_category_and_runs_terminal_cleanup(self):
        production = MagicMock()
        production._path_executor._plate_layout_service = self.layout
        ctx = PaintExecutionContext(production, lambda: False, PaintExecutionControl())
        with patch('src.robot_systems.paint.processes.paint.workflow.machine_factory.handle_prepare_dropoff',
                   side_effect=TrayLayoutChangedError()):
            machine = PaintExecutionMachineFactory().build(ctx, initial_state=PaintExecutionState.PREPARE_DROPOFF)
            machine.start_execution()
        self.assertIs(ctx.tray_failure.code, TrayErrorCode.LAYOUT_CHANGED)
        self.assertFalse(ctx.result_ok)
        self.assertIsNone(machine.get_snapshot().last_error)
        production._restore_brightness.assert_called_once()


class TestTrayStartController(unittest.TestCase):
    def controller(self, confirmed):
        model = MagicMock()
        model.get_drying_mode.return_value = "manual"
        model.start.side_effect = [TrayConfirmationRequiredError(), DashboardState(process_state="running")]
        model.confirm_empty_tray.return_value = DashboardCommandResult(True, "A new tray is ready.")
        view = MagicMock()
        view.ask_empty_tray_confirmation.return_value = confirmed
        controller = object.__new__(PaintDashboardController)
        controller._model = model
        controller._view = view
        return controller, model, view

    def test_confirm_continues_requested_start_once(self):
        controller, model, view = self.controller(True)
        controller._on_start()
        model.confirm_empty_tray.assert_called_once()
        self.assertEqual(model.start.call_count, 2)
        view.apply_dashboard_state.assert_called_once()

    def test_cancel_or_dismiss_does_not_confirm_or_retry_start(self):
        controller, model, view = self.controller(False)
        controller._on_start()
        model.confirm_empty_tray.assert_not_called()
        self.assertEqual(model.start.call_count, 1)
        view.apply_dashboard_state.assert_not_called()

    def test_confirmation_failure_does_not_retry_start(self):
        controller, model, view = self.controller(True)
        model.confirm_empty_tray.return_value = DashboardCommandResult(False, "busy", failure=TrayBusyError().as_failure())
        controller._on_start()
        self.assertEqual(model.start.call_count, 1)
        view.show_warning.assert_called_once()

    def test_other_tray_failure_does_not_prompt_for_unknown_occupancy(self):
        controller, model, view = self.controller(True)
        model.start.side_effect = TrayLayoutChangedError()
        controller._on_start()
        view.ask_empty_tray_confirmation.assert_not_called()
        view.show_warning.assert_called_once()


class TestTrayConfirmationDialog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PyQt6.QtWidgets import QApplication
        cls.app = QApplication.instance() or QApplication([])

    def test_explicit_confirm_cancel_and_window_dismissal(self):
        from PyQt6.QtCore import QTimer
        from PyQt6.QtWidgets import QPushButton, QWidget
        from src.robot_systems.paint.applications.dashboard.view.paint_dashboard_view import PaintDashboardView
        parent = QWidget()
        parent._translate_text = PaintDashboardView._translate_text
        for action, expected in [("confirm_empty", True), ("cancel", False), (None, False)]:
            with self.subTest(action=action):
                def choose():
                    dialog = self.app.activeModalWidget()
                    if action is None:
                        dialog.reject()
                    else:
                        dialog.findChild(QPushButton, "warningAction_" + action).click()
                QTimer.singleShot(0, choose)
                self.assertEqual(PaintDashboardView.ask_empty_tray_confirmation(parent), expected)
        parent.deleteLater()

    def test_dialog_uses_current_language_for_every_profile(self):
        import json
        from pathlib import Path
        from PyQt6.QtCore import QTimer
        from PyQt6.QtWidgets import QPushButton, QWidget
        from src.engine.localization.dict_translator import DictTranslator
        from src.robot_systems.paint.applications.dashboard.view.paint_dashboard_view import PaintDashboardView
        parent = QWidget()
        parent._translate_text = PaintDashboardView._translate_text
        root = Path(__file__).resolve().parents[3] / "src/robot_systems"
        for profile in ("paint", "paint_tray_dry", "paint_auto_dry"):
            for language in ("en", "bg"):
                with self.subTest(profile=profile, language=language):
                    catalog = json.loads((root / profile / "storage/translations" / (language + ".json")).read_text())
                    translator = DictTranslator(catalog)
                    self.app.installTranslator(translator)
                    captured = []
                    def dismiss():
                        dialog = self.app.activeModalWidget()
                        captured.append(dialog.findChild(QPushButton, "warningAction_confirm_empty").text())
                        dialog.reject()
                    try:
                        QTimer.singleShot(0, dismiss)
                        self.assertFalse(PaintDashboardView.ask_empty_tray_confirmation(parent))
                        self.assertEqual(captured, [catalog["PaintDashboard"]["Tray is empty — Start"]])
                    finally:
                        self.app.removeTranslator(translator)
        parent.deleteLater()
