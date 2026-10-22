"""No-argument desktop entry point; never imports machine bootstrap."""
import sys
from pathlib import Path
from PyQt6.QtCore import QCoreApplication, QEvent
from PyQt6.QtWidgets import QApplication, QMainWindow
from src.engine.localization.localization_service import LocalizationService
from src.engine.diagnostics.runtime import default_directory
from .diagnostics_application_factory import DiagnosticsApplicationFactory
from .service.diagnostics_application_service import DiagnosticsApplicationService


class _Window(QMainWindow):
    def retranslateUi(self):
        self.setWindowTitle(QCoreApplication.translate('DiagnosticsView', 'Machine diagnostics')
                            or 'Machine diagnostics')

    def changeEvent(self, event):
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)

    def closeEvent(self, event):
        if not self.centralWidget().can_close():
            event.ignore()
            return
        self.centralWidget().clean_up()
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    localization = LocalizationService(Path(__file__).parent / 'localization',
        state_file=str(default_directory().parent / 'diagnostics-viewer-language.json'))
    localization.set_language(localization.get_language())
    widget = DiagnosticsApplicationFactory().build(DiagnosticsApplicationService())
    widget.set_language(localization.get_language())
    widget.language_requested.connect(localization.set_language)
    window = _Window()
    window.setCentralWidget(widget)
    screen = app.primaryScreen()
    if screen is not None:
        available = screen.availableGeometry()
        window.resize(min(1360, available.width()), min(900, available.height()))
    else:
        window.resize(1360, 900)
    window.retranslateUi()
    app.aboutToQuit.connect(widget.clean_up)
    window.show()
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
