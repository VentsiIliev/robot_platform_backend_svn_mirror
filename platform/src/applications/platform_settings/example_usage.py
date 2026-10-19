"""Run Platform Settings without changing the host configuration."""

import sys

from PyQt6.QtWidgets import QApplication, QMainWindow

from src.applications.platform_settings.platform_settings_factory import PlatformSettingsFactory
from src.applications.platform_settings.service.stub_platform_settings_service import (
    StubPlatformSettingsService,
)


def run_standalone() -> None:
    app = QApplication(sys.argv)
    widget = PlatformSettingsFactory().build(StubPlatformSettingsService())
    window = QMainWindow()
    window.setCentralWidget(widget)
    window.resize(1280, 900)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_standalone()
