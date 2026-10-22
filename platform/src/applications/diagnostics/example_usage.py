"""Standalone UI development with a deterministic service, without hardware."""
import sys
from pathlib import Path

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from PyQt6.QtWidgets import QApplication
from src.applications.diagnostics.diagnostics_application_factory import DiagnosticsApplicationFactory
from src.applications.diagnostics.service.stub_diagnostics_service import StubDiagnosticsService


def run_standalone():
    app = QApplication.instance() or QApplication(sys.argv)
    widget = DiagnosticsApplicationFactory().build(StubDiagnosticsService())
    widget.resize(1280, 900)
    widget.show()
    app.aboutToQuit.connect(widget.clean_up)
    sys.exit(app.exec())


if __name__ == '__main__':
    run_standalone()
