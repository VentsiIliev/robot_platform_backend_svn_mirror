import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QLabel, QMessageBox, QPushButton

from src.applications.base.styled_message_box import (
    ActionWarningDialog, DialogAction, make_warning, show_warning,
)


class TestStyledMessageBox(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def test_action_warning_returns_chosen_button_and_allows_optional_sections(self) -> None:
        actions = (
            DialogAction("retry", "Scan again", primary=True),
            DialogAction("dismiss", "Dismiss", full_width=True),
        )
        def choose_retry() -> None:
            dialog = QApplication.activeModalWidget()
            self.assertIsNone(dialog.findChild(QPushButton, "warningAction_open_library"))
            self.assertIsNone(dialog.findChild(QLabel, "warningGuidance"))
            dialog.findChild(QPushButton, "warningAction_retry").click()

        QTimer.singleShot(0, choose_retry)
        selected = show_warning(
            None, "Workpiece not recognized", "No match",
            heading="PAINTING STOPPED", actions=actions,
        )

        self.assertEqual(selected, "retry")

    def test_collision_message_and_details_fit_at_minimum_dialog_width(self) -> None:
        text = ("Robot motion is held. Remove the obstruction, then release the "
                "collision hold when it is safe to move again.\n\n"
                "collision detected on Joint_3 by cpp_realtime_dynamics; operator acknowledgement required")
        dialog = ActionWarningDialog(
            None, "Collision Detected", text, heading="Collision Detected",
            actions=(DialogAction("keep", "Keep Motion Held"),
                     DialogAction("release", "Release Collision Hold", primary=True)))
        self.addCleanup(dialog.close)
        dialog.resize(540, 100)
        dialog.show()
        self.app.processEvents()
        body = dialog.findChild(QLabel, "warningBody")
        self.assertEqual(body.text(), text)
        self.assertGreaterEqual(body.height(), body.heightForWidth(body.width()))
        button = dialog.findChild(QPushButton, "warningAction_release")
        self.assertLess(body.geometry().bottom(), button.geometry().top())
        self.assertLessEqual(button.geometry().bottom(), dialog.height())
        dialog.grab().save("/tmp/zeroerr-warning-layout-preview.png")

    def test_optional_multiline_sections_fit_without_clipping(self) -> None:
        dialog = ActionWarningDialog(
            None, "Collision Detected", "Robot motion is held.", heading="Collision Detected",
            guidance="Remove the obstruction and verify the robot is safe. " * 4,
            status="The collision observer is waiting for stationary joints and clear torque. " * 3,
            actions=(DialogAction("keep", "Keep Motion Held"),))
        self.addCleanup(dialog.close)
        dialog.show()
        self.app.processEvents()
        for name in ("warningBody", "warningGuidance", "warningStatus"):
            label = dialog.findChild(QLabel, name)
            self.assertGreaterEqual(label.height(), label.heightForWidth(label.width()), name)

    def test_plain_warning_keeps_message_box_api(self) -> None:
        self.assertIsInstance(make_warning(None, "Warning", "Text"), QMessageBox)


if __name__ == "__main__":
    unittest.main()
