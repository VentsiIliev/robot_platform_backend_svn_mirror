"""Standalone developer screen with an in-memory stub; never opens hardware."""

import sys

from PyQt6.QtWidgets import QApplication, QMainWindow

from src.robot_systems.paint.applications.paint_head_detector_setup.paint_head_detector_setup_application_factory import (
    PaintHeadDetectorSetupApplicationFactory,
)
from src.robot_systems.paint.applications.paint_head_detector_setup.service.stub_paint_head_detector_setup_service import (
    StubPaintHeadDetectorSetupService,
)


def main() -> int:
    app = QApplication(sys.argv)
    service = StubPaintHeadDetectorSetupService()
    widget = PaintHeadDetectorSetupApplicationFactory().build(service)
    window = QMainWindow()
    window.setCentralWidget(widget)
    window.resize(1280, 1024)
    window.show()
    result = app.exec()
    widget.clean_up()
    return result


if __name__ == "__main__":
    raise SystemExit(main())
