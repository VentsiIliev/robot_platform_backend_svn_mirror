"""Exercise the standalone studio against synthetic frames, without robot I/O."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from scripts.run_platform import prepare_qt_environment
prepare_qt_environment()
import tempfile
import time
import unittest
from pathlib import Path
import ezdxf
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt
from src.applications.contour_dxf.contour_dxf_factory import ContourDXFFactory
from src.applications.contour_dxf.service.stub_contour_dxf_service import StubContourDXFService
from src.applications.contour_dxf.standalone import _StudioWindow
from src.engine.localization.localization_service import LocalizationService


class StudioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setStyle('Fusion')

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.service = StubContourDXFService(self.temp.name)
        self.localization = LocalizationService('src/applications/contour_dxf/localization', state_file=self.temp.name + '/language.json')
        self.localization.set_language('en')
        self.view = ContourDXFFactory().build(self.service)
        self.window = _StudioWindow(self.view)
        self.window.show()
        self.wait_idle()
        self.view.stop_refresh()

    def wait_idle(self):
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            self.app.processEvents()
            if not self.view._controller.has_active_operations():
                self.app.processEvents()
                return
            time.sleep(.005)
        self.fail('GUI operation did not finish')

    def tearDown(self):
        self.view.clean_up()
        self.window.close()
        self.app.processEvents()
        self.app.removeTranslator(self.localization._current_translator)
        self.temp.cleanup()

    def test_capture_calibrate_export_and_overwrite_protection(self):
        self.assertFalse(self.view._export_button.isEnabled())
        self.view._calibrate_button.click()
        self.wait_idle()
        self.assertEqual(self.view._status, 'calibrated')
        self.assertFalse(self.view._export_button.isEnabled())
        self.view._capture_button.click()
        self.wait_idle()
        self.assertEqual(self.view._status, 'captured')
        self.assertTrue(self.view._export_button.isEnabled())
        self.assertEqual(self.view._metric_values[0].text(), '120.00 mm')
        destination = Path(self.temp.name) / 'part.dxf'
        self.view.export_requested.emit(str(destination))
        self.wait_idle()
        doc = ezdxf.readfile(destination)
        self.assertTrue(doc.modelspace().query('LWPOLYLINE')[0].closed)
        self.assertFalse(doc.audit().has_errors)
        original = destination.read_bytes()
        self.view.export_requested.emit(str(destination))
        self.wait_idle()
        self.assertEqual(self.view._status, 'error')
        self.assertEqual(destination.read_bytes(), original)
        if os.environ.get('CONTOUR_STUDIO_SCREENSHOT'):
            self.view.set_status('captured')
            self.view._controller._on_refresh()
            deadline = time.monotonic() + 1
            while self.view._controller._frame_busy and time.monotonic() < deadline:
                self.app.processEvents()
                time.sleep(.005)
            self.app.processEvents()
            self.window.grab().save(os.environ['CONTOUR_STUDIO_SCREENSHOT'])

    def test_rejected_reference_keeps_correction_and_blocks_export(self):
        self.view._capture_button.click()
        self.wait_idle()
        self.view.set_reference(120, 200, 2)
        self.view._calibrate_button.click()
        self.wait_idle()
        self.assertEqual(self.view._status, 'error')
        self.assertEqual(self.service.get_info().correction, 1)
        self.assertFalse(self.view._export_button.isEnabled())

    def test_initial_and_runtime_translation_and_disconnect(self):
        self.assertEqual(self.view._capture_button.text(), 'Capture contour')
        self.localization.set_language('bg')
        self.app.processEvents()
        self.assertEqual(self.view._capture_button.text(), 'Заснеми контур')
        self.assertEqual(self.view._status_label.text(), 'Готово за заснемане')
        self.view._camera.click()
        self.wait_idle()
        self.assertFalse(self.view._capture_button.isEnabled())
        self.assertEqual(self.view._camera.text(), 'Свържи камерата')
        self.localization.set_language('en')
        self.app.processEvents()
        self.assertEqual(self.view._camera.text(), 'Connect camera')

    def test_bulgarian_initial_render_and_touch_numeric_fields(self):
        self.view.clean_up()
        self.localization.set_language('bg')
        self.view = ContourDXFFactory().build(self.service)
        self.window.setCentralWidget(self.view)
        self.wait_idle()
        self.view.stop_refresh()
        self.assertEqual(self.view._capture_button.text(), 'Заснеми контур')
        for field, text, expected in [(self.view._reference_width, '125.5', 125.5),
                                      (self.view._tolerance, '3.5', 3.5)]:
            spin = field._spin
            spin.setFocus()
            spin.selectAll()
            QTest.keyClicks(spin, text)
            QTest.keyClick(spin, Qt.Key.Key_Return)
            self.assertAlmostEqual(field.value(), expected)
            field._increase.click()
            self.assertGreater(field.value(), expected)
