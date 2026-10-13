import sys
from pathlib import Path
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWebEngineWidgets import QWebEngineView

class FluidWindow(QWebEngineView):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PyQt6 - Original WebGL Fluid Smoke')
        self.resize(1200, 800)
        self.load(QUrl.fromLocalFile(str(Path(__file__).resolve().parent / 'index.html')))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FluidWindow()
    window.show()
    sys.exit(app.exec())
