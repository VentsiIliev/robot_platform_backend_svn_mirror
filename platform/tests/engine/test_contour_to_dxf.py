from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import ezdxf
import numpy as np

from src.engine.geometry.contour_to_dxf import write_contour_dxf
from src.engine.geometry.rectangle_scale_calibration import calibrate_rectangle_scale


class ContourDXFTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / 'contour.dxf'
        self.contour = np.array([[10, 20], [30, 20], [30, 30], [10, 30]], dtype=float)

    def test_readable_closed_mm_polyline_and_unchanged_input(self):
        original = self.contour.copy()
        self.assertEqual(write_contour_dxf(self.path, self.contour, 0.5), self.path)
        document = ezdxf.readfile(self.path)
        self.assertFalse(document.audit().has_errors)
        self.assertEqual(document.header['$INSUNITS'], 4)
        entities = list(document.modelspace())
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0].dxftype(), 'LWPOLYLINE')
        self.assertTrue(entities[0].closed)
        self.assertEqual(entities[0].dxf.layer, 'CONTOUR')
        np.testing.assert_allclose(list(entities[0].get_points('xy')), [[0, 5], [10, 5], [10, 0], [0, 0]])
        np.testing.assert_array_equal(self.contour, original)

    def test_opencv_input_and_repeated_closing_vertex(self):
        contour = np.vstack((self.contour, self.contour[0])).reshape(-1, 1, 2)
        write_contour_dxf(self.path, contour)
        document = ezdxf.readfile(self.path)
        self.assertEqual(document.header['$INSUNITS'], 0)
        self.assertEqual(len(document.modelspace().query('LWPOLYLINE')[0]), 4)

    def test_existing_output_is_preserved(self):
        self.path.write_text('original')
        with self.assertRaises(FileExistsError):
            write_contour_dxf(self.path, self.contour)
        self.assertEqual(self.path.read_text(), 'original')

    def test_extension_duplicate_cleanup_and_initial_view(self):
        contour = np.repeat(self.contour, 2, axis=0)
        saved = write_contour_dxf(self.path.with_suffix(''), contour, 0.5)
        self.assertEqual(saved, self.path)
        document = ezdxf.readfile(saved)
        self.assertEqual(document.dxfversion, 'AC1015')
        self.assertEqual(len(document.modelspace().query('LWPOLYLINE')[0]), 4)
        self.assertGreater(document.viewports.get('*Active')[0].dxf.height, 5)

    def test_failed_validation_leaves_no_export_or_temporary_file(self):
        with patch('src.engine.geometry.contour_to_dxf.ezdxf.readfile', side_effect=ValueError('Invalid DXF')):
            with self.assertRaisesRegex(ValueError, 'Invalid DXF'):
                write_contour_dxf(self.path, self.contour, 0.5)
        self.assertEqual(list(self.path.parent.iterdir()), [])

    def test_invalid_geometry_and_scale_create_no_file(self):
        for points, scale in (([], 1), ([[0, 0], [1, 0], [2, 0]], 1),
                              ([[0, 0], [1, 0], [float('nan'), 1]], 1),
                              (self.contour, 0), (self.contour, float('inf'))):
            with self.subTest(points=points, scale=scale), self.assertRaises(ValueError):
                write_contour_dxf(self.path, points, scale)
            self.assertFalse(self.path.exists())


class RectangleScaleTests(unittest.TestCase):
    def test_known_uniform_scale_and_swapped_rectangle_axes(self):
        for measured in ((50, 100), (100, 50)):
            result = calibrate_rectangle_scale(measured, (120, 60))
            self.assertAlmostEqual(result.correction, 1.2)
            np.testing.assert_allclose(result.corrected_size_mm, (60, 120))
            np.testing.assert_allclose(result.residual_mm, (0, 0))

    def test_inconsistent_axes_produce_visible_residuals(self):
        result = calibrate_rectangle_scale((97.83, 116.90), (100, 120))
        self.assertAlmostEqual(result.correction, (97.83 * 100 + 116.90 * 120) / (97.83**2 + 116.90**2))
        self.assertNotEqual(result.residual_mm, (0, 0))

    def test_invalid_dimensions_rejected(self):
        for measured, reference in (((0, 2), (1, 2)), ((1, 2), (-1, 2)),
                                    ((1, float('nan')), (1, 2)), ((1,), (1, 2))):
            with self.subTest(measured=measured), self.assertRaises(ValueError):
                calibrate_rectangle_scale(measured, reference)
