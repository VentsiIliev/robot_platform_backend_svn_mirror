from src.robot_systems.paint.processes.paint.results import PaintOperationResult, PaintOutcome, PaintFailureCode
import threading
import unittest
from unittest.mock import MagicMock, patch

from src.robot_systems.paint.applications.dashboard.service.paint_dashboard_service import (
    PaintDashboardService,
)
from src.robot_systems.paint.processes.paint.paint_process import PaintProcess
from src.shared_contracts.events.process_events import ProcessState


class TestPaintProcessLifecycle(unittest.TestCase):
    def _start_blocked_run(self, outcome=(True, "Paint completed")):
        production_entered = threading.Event()
        production_release = threading.Event()
        stop_entered = threading.Event()
        stop_release = threading.Event()
        callbacks = []
        production = MagicMock()
        robot = MagicMock()

        def run_once(should_stop, **_kwargs):
            callbacks.append(should_stop)
            production_entered.set()
            if not production_release.wait(5):
                raise TimeoutError("Test did not release production worker")
            if isinstance(outcome, Exception):
                raise outcome
            return (PaintOperationResult(PaintOutcome.COMPLETED, outcome[1]) if outcome[0]
                    else PaintOperationResult.failed(PaintFailureCode.MOTION, "production", outcome[1]))

        def stop_motion():
            stop_entered.set()
            if not stop_release.wait(5):
                raise TimeoutError("Test did not release hardware-stop worker")

        production.run_once_result.side_effect = run_once
        robot.stop_motion.side_effect = stop_motion
        process = PaintProcess(production, MagicMock(), robot_service=robot)

        def cleanup():
            production_release.set()
            stop_release.set()
            for thread in (process._thread, process._stop_thread):
                if thread is not None:
                    thread.join(2)

        self.addCleanup(cleanup)
        process.start()
        self.assertTrue(production_entered.wait(2))
        return process, production, callbacks, production_release, stop_entered, stop_release

    def test_all_start_paths_wait_for_both_workers_in_either_completion_order(self):
        for production_finishes_first in (True, False):
            with self.subTest(production_finishes_first=production_finishes_first):
                process, production, callbacks, run_release, stop_entered, stop_release = (
                    self._start_blocked_run()
                )
                dashboard = PaintDashboardService(process)
                process.stop()
                self.assertTrue(stop_entered.wait(2))
                first_worker = process._thread
                first_stop_worker = process._stop_thread

                def assert_restart_blocked():
                    self.assertTrue(process.is_stopping)
                    self.assertFalse(dashboard.load_state().can_start)
                    process.start()
                    process.resume()
                    self.assertFalse(process.start_manual_single_cycle())
                    self.assertFalse(process.start_adjustment_cycle())
                    self.assertIs(process._thread, first_worker)
                    self.assertEqual(production.run_once_result.call_count, 1)
                    self.assertTrue(callbacks[0]())
                    self.assertEqual(process.state, ProcessState.STOPPED)

                assert_restart_blocked()
                if production_finishes_first:
                    run_release.set()
                    first_worker.join(2)
                    self.assertFalse(first_worker.is_alive())
                else:
                    stop_release.set()
                    first_stop_worker.join(2)
                    self.assertFalse(first_stop_worker.is_alive())
                assert_restart_blocked()

                run_release.set()
                stop_release.set()
                first_worker.join(2)
                first_stop_worker.join(2)
                self.assertFalse(process.is_stopping)
                self.assertTrue(dashboard.load_state().can_start)

                entered_again = threading.Event()
                release_again = threading.Event()
                self.addCleanup(release_again.set)

                def next_run(should_stop):
                    self.assertFalse(should_stop())
                    entered_again.set()
                    release_again.wait(2)
                    return PaintOperationResult(PaintOutcome.COMPLETED, "Paint completed")

                production.run_once_result.side_effect = next_run
                process.start()
                self.assertTrue(entered_again.wait(2))
                self.assertIsNot(process._thread, first_worker)
                self.assertTrue(callbacks[0]())
                release_again.set()
                process._thread.join(2)
                process._stop_thread.join(2)
                self.assertEqual(production.run_once_result.call_count, 2)

    def test_reset_cannot_revive_cancelled_run_or_publish_late_result(self):
        for outcome in ((True, "done"), (False, "late failure"), RuntimeError("late error")):
            with self.subTest(outcome=outcome):
                process, production, callbacks, run_release, stop_entered, stop_release = (
                    self._start_blocked_run(outcome)
                )
                process.stop()
                self.assertTrue(stop_entered.wait(2))
                process.reset_errors()
                self.assertEqual(process.state, ProcessState.IDLE)
                self.assertFalse(process._stopping)
                self.assertTrue(callbacks[0]())
                self.assertFalse(PaintDashboardService(process).load_state().can_start)
                process.start()
                self.assertEqual(production.run_once_result.call_count, 1)
                process._messaging.publish.reset_mock()
                run_release.set()
                stop_release.set()
                process._thread.join(2)
                process._stop_thread.join(2)
                self.assertEqual(process.state, ProcessState.IDLE)
                process._messaging.publish.assert_not_called()

    def test_retry_is_rejected_before_reset_while_old_workers_remain(self):
        process, production, _callbacks, _release, stop_entered, _stop_release = (
            self._start_blocked_run()
        )
        process.stop()
        self.assertTrue(stop_entered.wait(2))
        process.set_error("Unknown workpiece")
        production.can_retry_unmatched_workpiece.return_value = True
        self.assertFalse(process.retry_unmatched_workpiece())
        self.assertEqual(process.state, ProcessState.ERROR)
        self.assertEqual(production.run_once_result.call_count, 1)

    def test_start_while_paused_resumes_existing_worker(self):
        process, production, _callbacks, _release, _entered, _stop_release = (
            self._start_blocked_run()
        )
        worker = process._thread
        process.pause()
        process.start()
        self.assertEqual(process.state, ProcessState.RUNNING)
        self.assertIs(process._thread, worker)
        self.assertEqual(production.run_once_result.call_count, 1)
        production.resume_current_phase.assert_called_once_with()

    def test_dashboard_reports_delayed_cleanup_without_changing_process_state(self):
        process, _production, _callbacks, _release, stop_entered, _stop_release = (
            self._start_blocked_run()
        )
        with patch(
            "src.robot_systems.paint.processes.paint.paint_process.monotonic",
            return_value=100.0,
        ) as clock:
            process.stop()
            self.assertTrue(stop_entered.wait(2))
            dashboard = PaintDashboardService(process)
            state = dashboard.load_state()
            self.assertEqual(state.process_state, "stopped")
            self.assertFalse(state.can_start)
            self.assertEqual(state.status_lines, ["Waiting for paint stopping to finish."])
            self.assertEqual(state.card_states[3].note, state.status_lines[0])
            clock.return_value = 110.0
            self.assertEqual(
                dashboard.load_state().status_lines,
                ["Stopping is taking longer than expected."],
            )

    def test_dashboard_button_stays_disabled_until_workers_exit(self):
        from PyQt6.QtWidgets import QApplication
        from src.robot_systems.paint.applications.dashboard.config import (
            PAINT_DASHBOARD_ACTIONS,
            PAINT_DASHBOARD_CARDS,
            PaintDashboardConfig,
            PaintDashboardUiConfig,
        )
        from src.robot_systems.paint.applications.dashboard.view.paint_dashboard_view import (
            PaintDashboardView,
        )
        from src.robot_systems.paint.applications.dashboard.ui.paint_card_factory import (
            PaintCardFactory,
        )

        app = QApplication.instance() or QApplication([])
        self._app = app
        view = PaintDashboardView(
            config=PaintDashboardConfig(),
            action_buttons=PAINT_DASHBOARD_ACTIONS,
            cards=PaintCardFactory().build_cards(PAINT_DASHBOARD_CARDS),
            ui_config=PaintDashboardUiConfig(show_camera_preview=False),
        )
        self.addCleanup(view.deleteLater)
        process, _production, _callbacks, release, stop_entered, stop_release = (
            self._start_blocked_run()
        )
        dashboard = PaintDashboardService(process)
        process.stop()
        self.assertTrue(stop_entered.wait(2))
        view.apply_dashboard_state(dashboard.load_state())
        self.assertFalse(view._dashboard.control_buttons.start_btn.isEnabled())
        self.assertEqual(
            view._cards_by_id[3]._note, "Waiting for paint stopping to finish."
        )
        release.set()
        process._thread.join(2)
        view.apply_dashboard_state(dashboard.load_state())
        self.assertFalse(view._dashboard.control_buttons.start_btn.isEnabled())
        stop_release.set()
        process._stop_thread.join(2)
        view.apply_dashboard_state(dashboard.load_state())
        self.assertTrue(view._dashboard.control_buttons.start_btn.isEnabled())
        self.assertEqual(view._cards_by_id[3]._note, "Paint job stopped")
        app.processEvents()
