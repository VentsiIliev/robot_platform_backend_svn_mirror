import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication, QPushButton, QWidget

from src.applications.base.onboarding import OnboardingStep, OnboardingTour


class OnboardingTourTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.host = QWidget()
        self.host.resize(900, 600)
        self.target = QPushButton("Target", self.host)
        self.target.setGeometry(100, 100, 240, 80)
        self.host.show()
        self._app.processEvents()

    def tearDown(self) -> None:
        self.host.close()
        self.host.deleteLater()
        self._app.processEvents()

    def test_start_and_finish_manage_overlay_lifecycle(self) -> None:
        tour = OnboardingTour(
            host_provider=lambda: self.host,
            steps=(OnboardingStep(lambda: self.target, "Title", "Body"),),
            translator=lambda source: source,
            parent=self.host,
        )

        tour.start()
        self._app.processEvents()

        self.assertIsNotNone(tour._overlay)
        self.assertTrue(tour._overlay.isVisible())

        tour.next()
        self._app.processEvents()

        self.assertIsNone(tour._overlay)

    def test_hidden_targets_are_skipped(self) -> None:
        hidden = QPushButton("Hidden", self.host)
        hidden.hide()
        tour = OnboardingTour(
            host_provider=lambda: self.host,
            steps=(
                OnboardingStep(lambda: hidden, "Hidden", "Hidden body"),
                OnboardingStep(lambda: self.target, "Visible", "Visible body"),
            ),
            translator=lambda source: source,
            parent=self.host,
        )

        tour.start()
        self._app.processEvents()

        self.assertEqual(1, tour._index)
        self.assertEqual("Visible", tour._overlay._title.text())

    def test_non_spotlight_step_centers_card_and_dims_entire_host(self) -> None:
        tour = OnboardingTour(
            host_provider=lambda: self.host,
            steps=(
                OnboardingStep(
                    lambda: self.target,
                    "Welcome",
                    "Introduction",
                    spotlight=False,
                ),
            ),
            translator=lambda source: source,
            parent=self.host,
        )

        tour.start()
        self._app.processEvents()

        overlay = tour._overlay
        self.assertTrue(overlay._spotlight.isEmpty())
        self.assertLessEqual(abs(overlay._card.geometry().center().x() - overlay.rect().center().x()), 1)
        self.assertLessEqual(abs(overlay._card.geometry().center().y() - overlay.rect().center().y()), 1)

    def test_close_button_stops_tour(self) -> None:
        tour = OnboardingTour(
            host_provider=lambda: self.host,
            steps=(OnboardingStep(lambda: self.target, "Title", "Body"),),
            translator=lambda source: source,
            parent=self.host,
        )
        tour.start()
        self._app.processEvents()

        tour._overlay._close.click()
        self._app.processEvents()

        self.assertIsNone(tour._overlay)


if __name__ == "__main__":
    unittest.main()
