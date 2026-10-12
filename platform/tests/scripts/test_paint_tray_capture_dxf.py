"""Calibration persistence and capture-to-export flow without camera or robot."""
from concurrent.futures import Future
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import ezdxf
import numpy as np

from src.engine.geometry.rectangle_scale_calibration import calibrate_rectangle_scale

path = Path(__file__).resolve().parents[2] / 'scripts/paint_tray_capture_dxf.py'
spec = importlib.util.spec_from_file_location('paint_capture_dxf', path)
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)


class ImmediateWorker:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def submit(self, fn, *args):
        result = Future()
        result.set_result(fn(*args))
        return result


class CaptureScaleTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.path = self.root / 'scale_calibration_paint.json'
        self.context = capture.scale_calibration_context('paint', 1.0, None)

    def test_saved_correction_roundtrips_and_rejects_another_scale_or_area(self):
        result = calibrate_rectangle_scale((116.9, 97.83), (120, 100))
        capture.save_scale_correction(self.path, self.context, result)
        self.assertEqual(capture.load_scale_correction(self.path, self.context), result.correction)
        for context in (dict(self.context, area='magazine'), dict(self.context, base_mm_per_pixel=0.5)):
            with self.assertRaisesRegex(ValueError, 'does not match'):
                capture.load_scale_correction(self.path, context)

    def test_changed_nominal_geometry_file_invalidates_correction(self):
        geometry = self.root / 'geometry.json'
        geometry.write_text('{"ppm":1}')
        context = capture.scale_calibration_context('paint', 1.0, geometry)
        capture.save_scale_correction(self.path, context, calibrate_rectangle_scale((100, 50), (120, 60)))
        geometry.write_text('{"ppm":2}')
        with self.assertRaisesRegex(ValueError, 'does not match'):
            capture.load_scale_correction(self.path, capture.scale_calibration_context('paint', 1.0, geometry))

    def run_capture(self, size=(116.9, 97.83)):
        contour = np.array([[0, 0], [size[0], 0], [size[0], size[1]], [0, size[1]]])
        preview = np.zeros((20, 20, 3), dtype=np.uint8)
        vision = Mock()
        argv = ['capture', '--opencv', '--mm-per-pixel', '1', '--reference-size-mm', '120', '100',
                '--output-dir', str(self.root)]
        with (patch('sys.argv', argv), patch.object(capture, 'build_vision', return_value=vision),
              patch.object(capture, 'ThreadPoolExecutor', return_value=ImmediateWorker()),
              patch.object(capture, 'capture_geometry', return_value=(preview, contour, None, size)) as geometry,
              patch.object(capture.CaptureWindow, 'draw'), patch.object(capture.cv2, 'namedWindow'),
              patch.object(capture.cv2, 'setMouseCallback'), patch.object(capture.cv2, 'destroyAllWindows'),
              patch.object(capture.cv2, 'getWindowProperty', return_value=1),
              patch.object(capture.cv2, 'waitKey', side_effect=[32, -1, 32, -1, ord('q')]),
              patch('sys.stdout', new_callable=io.StringIO), patch('sys.stderr', new_callable=io.StringIO)):
            self.assertEqual(capture.main(), 0)
        vision.start.assert_called_once()
        vision.stop.assert_called_once()
        return geometry

    def test_reference_capture_saves_correction_then_next_capture_exports_mm_dxf(self):
        geometry = self.run_capture()
        self.assertFalse(geometry.call_args_list[0].args[2])
        self.assertTrue(geometry.call_args_list[1].args[2])
        correction = capture.load_scale_correction(self.path, self.context)
        self.assertAlmostEqual(geometry.call_args_list[1].args[1], correction)
        exports = list(self.root.glob('*.dxf'))
        self.assertEqual(len(exports), 1)  # Reference calibrates; only the part is exported.
        document = ezdxf.readfile(exports[0])
        self.assertEqual(document.header['$INSUNITS'], 4)
        self.assertFalse(document.audit().has_errors)

    def test_inconsistent_reference_preserves_previous_calibration(self):
        self.path.write_text('previous calibration')
        geometry = self.run_capture((100, 20))
        self.assertTrue(all(not call.args[2] for call in geometry.call_args_list))
        self.assertEqual(self.path.read_text(), 'previous calibration')
        self.assertEqual(list(self.root.glob('*.dxf')), [])
