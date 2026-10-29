"""Thread-safe dashboard reporting uses the existing primary-camera tab."""

import threading
import unittest
from dataclasses import replace
from unittest.mock import MagicMock

import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication, QLabel, QMenu, QTabWidget, QPushButton
from pl_gui.dashboard.widgets.RobotTrajectoryWidget import RobotTrajectoryWidget

from src.engine.core.i_messaging_service import IMessagingService
from src.robot_systems.paint.applications.dashboard.config import (
    PaintDashboardConfig,
    PaintDashboardUiConfig,
)
from src.robot_systems.paint.applications.dashboard.controller.paint_dashboard_controller import (
    PaintDashboardController,
)
from src.robot_systems.paint.applications.dashboard.dashboard_state import DashboardState
from src.robot_systems.paint.applications.dashboard.head_alignment_presentation import (
    GuideAvailability,
)
from src.robot_systems.paint.applications.dashboard.view.paint_dashboard_view import (
    PaintDashboardView,
)
from src.robot_systems.paint.applications.dashboard.ui.head_alignment_guide import (
    PaintHeadAlignmentGuide,
)
from src.robot_systems.paint.applications.dashboard.ui.head_alignment_popup import (
    PaintHeadAlignmentPopup,
)
from src.robot_systems.paint.contracts.events.paint_head_check_events import (
    PaintHeadCheckStatusEvent,
    PaintHeadCheckTopics,
    PaintHeadFeedbackMode,
)
from src.robot_systems.paint.contracts.paint_head_check.errors import (
    HeadInspectionFailure,
    HeadInspectionFailureCode,
)
from src.robot_systems.paint.contracts.paint_head_check.guidance import HeadRotationCorrection
from src.robot_systems.paint.contracts.paint_head_check.models import (
    HeadCheckContext,
    HeadCheckProgress,
    PaintHeadObservation,
    PaintHeadObservationReason,
    PaintHeadState,
)
from src.robot_systems.paint.paint_head_check.adapters.dashboard import (
    DashboardPaintHeadCheckObserver,
)
from tests.robot_systems.paint.test_head_check_settings_ui import CatalogTranslator
from tests.robot_systems.paint.test_head_check_alignment_guide import correction


def observation(state: PaintHeadState) -> PaintHeadObservation:
    return PaintHeadObservation(
        state, state, PaintHeadObservationReason.ALIGNED, 1, 1.0, 1.0, 1.0, 1, None, False
    )


class HeadCheckDashboardObserverTests(unittest.TestCase):
    def test_dashboard_reopening_replays_live_mode_and_cancellation_clears_its_pose(self) -> None:
        messaging = MagicMock(spec=IMessagingService)
        observer = DashboardPaintHeadCheckObserver(messaging)
        observer.start()
        replay = messaging.subscribe.call_args.args[1]
        observer.guidance_started()
        observer.guidance_observation(observation(PaintHeadState.PRESENT))
        replay(None)
        event = messaging.publish.call_args.args[1]
        self.assertIs(PaintHeadFeedbackMode.LIVE_GUIDANCE, event.mode)
        self.assertIs(PaintHeadState.PRESENT, event.last_observation.state)
        observer.guidance_ended()
        replay(None)
        event = messaging.publish.call_args.args[1]
        self.assertIs(PaintHeadFeedbackMode.GUIDANCE_ENDED, event.mode)
        self.assertIsNone(event.last_observation)
        observer.stop()

    def test_timeout_snapshot_retains_the_last_observation_for_replay(self) -> None:
        messaging = MagicMock(spec=IMessagingService)
        observer = DashboardPaintHeadCheckObserver(messaging)
        observer.start()
        replay = messaging.subscribe.call_args.args[1]
        missing = observation(PaintHeadState.MISSING)
        context = HeadCheckContext(HeadCheckProgress(0), 4, 1.0, missing)
        failure = HeadInspectionFailure(HeadInspectionFailureCode.TIMEOUT, "Timed out")
        observer.inspection_failed(failure, context)
        replay(None)
        status = messaging.publish.call_args.args[1]
        self.assertIs(failure, status.evidence)
        self.assertIs(missing, status.last_observation)
        observer.inspection_started(HeadCheckContext(HeadCheckProgress(0), 1, 0.0, None))
        self.assertIsNone(messaging.publish.call_args.args[1].last_observation)
        observer.stop()

    def test_status_replay_and_lifecycle_are_explicit(self) -> None:
        messaging = MagicMock(spec=IMessagingService)
        observer = DashboardPaintHeadCheckObserver(messaging)
        observer.start()
        observer.start()
        messaging.subscribe.assert_called_once()
        replay = messaging.subscribe.call_args.args[1]
        replay(None)
        messaging.publish.assert_not_called()
        context = HeadCheckContext(HeadCheckProgress(0), 1, 0.0, None)
        observer.inspection_started(context)
        self.assertEqual(PaintHeadCheckStatusEvent(1, None), messaging.publish.call_args.args[1])
        missing = observation(PaintHeadState.MISSING)
        observer.observation_received(missing, context)
        replay(None)
        self.assertEqual(
            (PaintHeadCheckTopics.STATUS, PaintHeadCheckStatusEvent(2, missing)),
            messaging.publish.call_args.args,
        )
        observer.stop()
        observer.stop()
        messaging.unsubscribe.assert_called_once_with(PaintHeadCheckTopics.REQUEST_STATUS, replay)


class HeadCheckDashboardUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.view = PaintDashboardView(
            config=PaintDashboardConfig(),
            action_buttons=[],
            cards=[],
            ui_config=PaintDashboardUiConfig(show_camera_preview=False, show_tray_camera_tab=True),
            camera_roles=("primary_vision", "auxiliary"),
        )
        self.view.resize(1280, 900)
        self.view.show()
        self.messaging = MagicMock(spec=IMessagingService)
        self.controller = PaintDashboardController(MagicMock(), self.view, self.messaging)
        self.controller._model.load.return_value = DashboardState(process_state="stopped")
        self.controller._active = True
        self.capture = MagicMock(wraps=self.view.set_head_alignment_feedback)
        self.view.set_head_alignment_feedback = self.capture
        self.camera = self.view.findChild(RobotTrajectoryWidget)
        self.page = self.camera.parentWidget()
        self.tabs = next(
            tab for tab in self.view.findChildren(QTabWidget) if tab.indexOf(self.page) >= 0
        )
        self.app.processEvents()
        self.addCleanup(self.dispose)

    def dispose(self) -> None:
        self.controller.stop()
        self.view.close()
        self.view.deleteLater()
        self.app.processEvents()

    def send(self, revision, state=None, *, live=False, correction_data=None):
        data = None if state is None else replace(observation(state), correction=correction_data)
        event = PaintHeadCheckStatusEvent(
            revision,
            data,
            mode=(PaintHeadFeedbackMode.LIVE_GUIDANCE if live else PaintHeadFeedbackMode.CHECK),
        )
        self.controller._on_head_check_status(event)
        self.app.processEvents()
        return event

    def popup(self):
        return self.view.findChild(PaintHeadAlignmentPopup)

    def card(self):
        return self.popup().findChild(PaintHeadAlignmentGuide)

    def test_normal_camera_tab_has_its_feed_and_selector_without_a_card_or_popup(self):
        self.tabs.setCurrentWidget(self.page)
        self.app.processEvents()
        self.assertTrue(self.view.is_camera_feed_visible())
        self.assertFalse(self.camera.isHidden())
        self.assertIsNone(self.page.findChild(PaintHeadAlignmentGuide))
        self.assertIsNone(self.popup())
        self.assertTrue(
            any(menu.parentWidget().isVisible() for menu in self.page.findChildren(QMenu))
        )
        for name in (
            "paintHeadCheckStatus",
            "paintHeadAlignmentLegend",
            "paintHeadAlignmentNotice",
        ):
            self.assertIsNone(self.page.findChild(QLabel, name))

    def test_misalignment_opens_one_modal_popup_with_only_close(self):
        self.send(1, PaintHeadState.MISALIGNED, correction_data=correction())
        popup = self.popup()
        self.assertTrue(popup.isVisible())
        self.assertTrue(popup.isModal())
        self.assertIs(popup, QApplication.activeModalWidget())
        buttons = popup.findChildren(QPushButton)
        self.assertEqual(1, len(buttons))
        self.assertEqual("Close", buttons[0].text())
        self.assertEqual("Paint head misaligned", self.card().status_text())
        self.assertIs(
            GuideAvailability.AVAILABLE, self.capture.call_args.args[0].guide.availability
        )
        for revision in range(2, 8):
            self.send(revision, PaintHeadState.MISALIGNED, live=True, correction_data=correction())
        self.assertEqual([popup], self.view.findChildren(PaintHeadAlignmentPopup))

    def test_popup_does_not_change_the_camera_tab_role_or_layout(self):
        for menu in self.view.findChildren(QMenu):
            for action in menu.actions():
                if action.data() == "auxiliary":
                    action.trigger()
        self.assertEqual("auxiliary", self.controller._selected_camera)
        self.tabs.setCurrentIndex(0)
        before_tab = self.tabs.currentIndex()
        before_camera = self.camera.geometry()
        self.send(1, PaintHeadState.MISSING)
        self.assertEqual(before_tab, self.tabs.currentIndex())
        self.assertEqual("auxiliary", self.controller._selected_camera)
        self.assertEqual(before_camera, self.camera.geometry())
        self.assertIsNot(self.card().parentWidget(), self.page)

    def test_worker_feedback_is_queued_to_the_popup_on_the_gui_thread(self):
        event = PaintHeadCheckStatusEvent(1, observation(PaintHeadState.MISSING))
        worker = threading.Thread(target=self.controller._on_head_check_status_raw, args=(event,))
        worker.start()
        worker.join()
        self.assertIsNone(self.popup())
        self.app.processEvents()
        self.assertTrue(self.popup().isVisible())
        self.assertEqual("Paint head missing", self.card().status_text())

    def test_close_dismisses_without_resuming_and_live_frames_do_not_reopen_it(self):
        self.send(1, PaintHeadState.MISALIGNED, correction_data=correction())
        popup = self.popup()
        QTest.mouseClick(popup.findChild(QPushButton), Qt.MouseButton.LeftButton)
        self.assertFalse(popup.isVisible())
        self.send(2, PaintHeadState.UNKNOWN, live=True)
        self.send(3, PaintHeadState.MISALIGNED, live=True, correction_data=correction())
        self.assertFalse(popup.isVisible())
        self.controller._model.start_process.assert_not_called()
        self.controller._model.resume_process.assert_not_called()
        self.controller._model.stop_process.assert_not_called()

    def test_starting_a_new_check_closes_old_popup_and_allows_a_new_warning(self):
        self.send(1, PaintHeadState.MISALIGNED, correction_data=correction())
        popup = self.popup()
        popup.reject()
        self.send(2)
        self.send(3, PaintHeadState.MISSING)
        self.assertIs(popup, self.popup())
        self.assertTrue(popup.isVisible())
        self.assertFalse(self.capture.call_args.args[0].guide.show_head_reference)
        self.assertIs(
            GuideAvailability.UNAVAILABLE, self.capture.call_args.args[0].guide.availability
        )

    def test_present_does_not_open_a_popup_but_live_alignment_updates_an_existing_popup(self):
        aligned = replace(
            correction(),
            translation_direction=None,
            rotation_direction=HeadRotationCorrection.NONE,
            translation_extent=0,
            rotation_extent=0,
        )
        self.send(1, PaintHeadState.PRESENT, correction_data=aligned)
        self.assertIsNone(self.popup())
        self.send(2, PaintHeadState.MISALIGNED, correction_data=correction())
        self.send(3, PaintHeadState.PRESENT, live=True, correction_data=aligned)
        self.assertTrue(self.popup().isVisible())
        self.assertTrue(self.capture.call_args.args[0].guide.aligned)
        self.assertEqual("Aligned — press Start to check and continue", self.card().notice_text())
        self.controller._model.start_process.assert_not_called()
        self.send(4, PaintHeadState.PRESENT, correction_data=aligned)
        self.assertFalse(self.popup().isVisible())

    def test_unknown_keeps_last_marker_grey_and_missing_hides_the_head(self):
        self.send(1, PaintHeadState.MISALIGNED, correction_data=correction())
        active = self.capture.call_args.args[0].guide
        self.send(2, PaintHeadState.UNKNOWN, live=True)
        unavailable = self.capture.call_args.args[0].guide
        self.assertIs(GuideAvailability.UNAVAILABLE, unavailable.availability)
        self.assertEqual(active.translation_direction, unavailable.translation_direction)
        self.assertFalse(unavailable.aligned)
        self.assertTrue(unavailable.show_head_reference)
        self.assertTrue(self.popup().isVisible())
        self.send(3, PaintHeadState.MISSING, live=True)
        self.assertFalse(self.capture.call_args.args[0].guide.show_head_reference)

    def test_camera_failure_and_guidance_end_never_leave_actionable_arrows(self):
        self.send(1, PaintHeadState.MISALIGNED, correction_data=correction())
        failure = HeadInspectionFailure(HeadInspectionFailureCode.TIMEOUT, "No frame")
        self.controller._on_head_check_status(
            PaintHeadCheckStatusEvent(2, failure, mode=PaintHeadFeedbackMode.LIVE_GUIDANCE)
        )
        self.assertIs(
            GuideAvailability.UNAVAILABLE, self.capture.call_args.args[0].guide.availability
        )
        self.assertEqual("Live alignment guidance unavailable", self.card().status_text())
        self.controller._on_head_check_status(
            PaintHeadCheckStatusEvent(3, None, mode=PaintHeadFeedbackMode.GUIDANCE_ENDED)
        )
        self.assertFalse(self.popup().isVisible())

    def test_closed_popup_never_reopens_on_language_change_and_translates_close(self):
        translator = CatalogTranslator("bg")
        self.app.installTranslator(translator)
        try:
            self.send(1, PaintHeadState.MISALIGNED, correction_data=correction())
            self.assertEqual("Боядисващата глава е разместена", self.card().status_text())
            self.assertEqual("Затвори", self.popup().findChild(QPushButton).text())
            self.popup().reject()
        finally:
            self.app.removeTranslator(translator)
        self.view.on_language_changed()
        self.app.processEvents()
        self.assertFalse(self.popup().isVisible())
        self.assertEqual("Paint head misaligned", self.card().status_text())
        self.assertEqual("Close", self.popup().findChild(QPushButton).text())

    def test_dashboard_cleanup_closes_popup_and_stale_events_cannot_replace_it(self):
        self.send(2, PaintHeadState.MISALIGNED, correction_data=correction())
        self.send(1, PaintHeadState.MISSING)
        self.assertEqual("Paint head misaligned", self.card().status_text())
        self.controller.stop()
        self.assertFalse(self.popup().isVisible())
        self.controller._on_head_check_status(
            PaintHeadCheckStatusEvent(3, observation(PaintHeadState.MISSING))
        )
        self.assertFalse(self.popup().isVisible())


if __name__ == "__main__":
    unittest.main()
