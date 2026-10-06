"""Standalone remote-support screen using a hardware-free stub."""


def run_standalone() -> None:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from PyQt6.QtWidgets import QApplication, QMainWindow
    from src.applications.remote_support.remote_support_application_factory import RemoteSupportApplicationFactory
    from src.applications.remote_support.service.stub_remote_support_service import StubRemoteSupportService

    app = QApplication(sys.argv)
    widget = RemoteSupportApplicationFactory().build(StubRemoteSupportService())
    window = QMainWindow()
    window.setCentralWidget(widget)
    window.resize(1280, 900)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_standalone()
