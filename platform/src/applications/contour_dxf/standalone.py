"""Standalone Qt host; service composition stays outside the MVC screen."""
from pathlib import Path
import sys

from PyQt6.QtWidgets import QApplication, QMainWindow
from src.engine.localization.localization_service import LocalizationService
from .contour_dxf_factory import ContourDXFFactory

class _StudioWindow(QMainWindow):
    def __init__(self, view):
        super().__init__()
        self._view = view
        self.setCentralWidget(view)
        self.setWindowTitle('PL PROJECT · Photo to DXF')
        self.resize(1440, 960)
        self.setMinimumSize(1100, 850)

    def closeEvent(self, event):
        if self._view._controller.has_active_operations():
            self._view.set_status('closing')
            event.ignore()
            return
        self._view.clean_up()
        event.accept()

def run_standalone(service, reference=(120, 100), tolerance=2, smooth=True):
    app = QApplication.instance() or QApplication(sys.argv[:1])
    app.setStyle('Fusion')
    catalog = Path(__file__).with_name('localization')
    info = service.get_info()
    localization = LocalizationService(str(catalog), state_file=str(Path(info.output_dir) / 'gui_language.json'))
    localization.set_language(localization.get_language())
    view = ContourDXFFactory().build(service)
    view.set_reference(*reference, tolerance)
    view.set_smoothing(smooth)
    view.language_requested.connect(localization.set_language)
    view._language.setCurrentIndex(view._language.findData(localization.get_language()))
    window = _StudioWindow(view)
    window.show()
    try:
        return app.exec()
    finally:
        view.clean_up()
        app.removeTranslator(localization._current_translator)
