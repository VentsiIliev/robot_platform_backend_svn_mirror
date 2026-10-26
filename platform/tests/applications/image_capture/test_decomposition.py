import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch

import cv2
import numpy as np

from src.applications.image_capture.processing.capture_decomposition import decompose_capture
from src.applications.image_capture.service.image_capture_application_service import ImageCaptureApplicationService


class DecompositionTests(unittest.TestCase):
    def test_rectangle_and_circle_are_processed_and_saved_with_source_indices(self):
        frame = np.full((180, 280, 3), 220, np.uint8)
        rectangle = np.array([[15, 15], [105, 15], [105, 85], [15, 85]], float)
        angles = np.linspace(0, 2*np.pi, 100, endpoint=False)
        circle = np.column_stack([200 + 40*np.cos(angles), 90 + 40*np.sin(angles)])
        vision = Mock()
        vision.capture_corrected_image.return_value = frame
        vision.detect_contours_for_image.return_value = [rectangle, circle]
        with TemporaryDirectory() as directory:
            service = ImageCaptureApplicationService(vision, directory)
            capture = service.capture()
            result = json.loads(capture.decomposition)
            self.assertEqual([c['contour_index'] for c in result['contours']], [0, 1])
            self.assertTrue(all(c['status'] == 'ok' for c in result['contours']))
            self.assertGreaterEqual(capture.line_count, 4)
            self.assertGreaterEqual(capture.arc_count, 1)
            self.assertEqual(capture.failed_contours, 0)
            self.assertNotEqual(capture.preview, capture.decomposition_preview)
            destination = Path(service.save_image(capture))
            saved = json.loads((destination / f'{destination.name}_decomposition.json').read_text())
            self.assertEqual(saved['contours'], result['contours'])
            self.assertEqual(saved['source'], f'{destination.name}.json')
            self.assertEqual((destination / f'{destination.name}_decomposition.png').read_bytes(), capture.decomposition_preview)
            self.assertEqual(cv2.imdecode(np.frombuffer(capture.decomposition_preview, np.uint8), 1).shape, frame.shape)
            with patch.object(Path, 'write_bytes', side_effect=[len(capture.image), OSError('disk full')]):
                with self.assertRaises(OSError):
                    service.save_image(capture)
            self.assertEqual(list(Path(directory).iterdir()), [destination])

    def test_bad_contour_is_reported_without_losing_other_results(self):
        frame = np.zeros((100, 100, 3), np.uint8)
        result, overlay, counts = decompose_capture(frame, [((1, 1), (1, 1), (1, 1))])
        data = json.loads(result)
        self.assertEqual(data['contours'][0]['status'], 'error')
        self.assertEqual(counts['failed_contours'], 1)
        self.assertEqual(overlay.shape, frame.shape)

    def test_no_contours_has_empty_result(self):
        result, _, counts = decompose_capture(np.zeros((20, 20, 3), np.uint8), [])
        self.assertEqual(json.loads(result)['contours'], [])
        self.assertEqual(counts['failed_contours'], 0)
