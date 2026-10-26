import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))


def run_standalone() -> None:
    from PyQt6.QtWidgets import QApplication, QMainWindow
    from src.applications.image_capture.image_capture_application_factory import ImageCaptureApplicationFactory
    from src.applications.image_capture.service.stub_image_capture_service import StubImageCaptureService

    app    = QApplication(sys.argv)
    widget = ImageCaptureApplicationFactory().build(StubImageCaptureService())

    window = QMainWindow()
    window.setCentralWidget(widget)
    window.resize(1280, 900)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_standalone()
