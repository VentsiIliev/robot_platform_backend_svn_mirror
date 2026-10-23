"""Regression checks for feature schemas, persisted artifacts and inference guards."""
import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np

from calibrate_slots import augment_frame, fit_forest, load_images
from slot_detector import (
    DetectorConfig, SlotConfig, SlotDetector, SlotState, forest_scores,
    feature_names, polygon_mask, preprocess, extract_features,
)


class DetectorTests(unittest.TestCase):
    def setUp(self):
        self.slot = SlotConfig('test', [(5, 5), (55, 5), (55, 55), (5, 55)])
        self.cfg = DetectorConfig(slots=[self.slot], vote_window=3)
        self.frame = np.full((64, 64, 3), 120, np.uint8)

    def test_legacy_schema_and_temporal_warmup(self):
        det = SlotDetector(self.cfg)
        det.set_reference(self.frame)
        self.assertEqual(len(det.features(self.frame)['test']), 3)
        self.assertEqual(det.update(self.frame)[0].state, SlotState.UNKNOWN)
        det.update(self.frame)
        self.assertEqual(det.update(self.frame)[0].state, SlotState.EMPTY)
        det.set_reference(self.frame)
        self.assertEqual(det.update(self.frame)[0].state, SlotState.UNKNOWN)

    def test_robust_features_and_empty_mask(self):
        self.slot.feature_version = 2
        prep = preprocess(self.frame, self.cfg)
        mask = polygon_mask(prep.shape, self.slot.polygon)
        for m in (mask, np.zeros_like(mask)):
            f = extract_features(prep, m, self.slot, prep, 0)
            self.assertEqual(f.shape, (len(feature_names(2)),))
            self.assertTrue(np.isfinite(f).all())
        with self.assertRaises(ValueError):
            feature_names(3)

    def test_missing_reference_stays_unknown(self):
        self.slot.feature_version = 2
        self.slot.weights = [0.] * len(feature_names(2))
        self.slot.bias = -10  # confident empty score must still be rejected
        det = SlotDetector(self.cfg)
        for _ in range(6):
            self.assertEqual(det.update(self.frame)[0].state, SlotState.UNKNOWN)

    def test_resolution_change_rejected(self):
        det = SlotDetector(self.cfg)
        det.set_reference(self.frame)
        with self.assertRaisesRegex(ValueError, 'resolution'):
            det.update(self.frame[:32, :32])

    def test_invalidated_reference_clears_history(self):
        det = SlotDetector(self.cfg)
        det.set_reference(self.frame)
        for _ in range(3):
            det.update(self.frame)
        det.invalidate_masks()
        self.assertFalse(det.has_reference('test'))
        self.assertEqual(det.update(self.frame)[0].state, SlotState.UNKNOWN)

    def test_model_reference_roundtrip_and_rebased_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            n = len(feature_names(2))
            self.slot.feature_version = 2
            X = np.vstack([np.zeros((15, n)), np.ones((15, n))]).astype(np.float32)
            model = fit_forest(X, np.r_[np.zeros(15), np.ones(15)])
            model.save(str(root / 'forest.xml'))
            self.slot.model_path = str(root / 'forest.xml')
            self.slot.reference_path = str(root / 'reference.npz')
            np.savez_compressed(root / 'reference.npz', norm=preprocess(self.frame, self.cfg),
                                std=0., polygon=self.slot.polygon,
                                preprocessing=[2., 4, 5, 35, 40, 120])
            self.cfg.save(root / 'config.json')
            loaded = DetectorConfig.load(root / 'config.json')
            det = SlotDetector(loaded)
            f = det.features(self.frame)['test']
            self.assertAlmostEqual(det.update(self.frame)[0].score, forest_scores(model, f[None])[0])
            self.assertTrue(det.has_reference('test'))
            (root / 'nested').mkdir()
            loaded.save(root / 'nested' / 'moved.json')
            self.assertTrue(SlotDetector(DetectorConfig.load(root / 'nested' / 'moved.json')).has_reference('test'))
            loaded.slots[0].polygon[0] = (6, 6)
            with self.assertRaisesRegex(ValueError, 'polygon changed'):
                SlotDetector(loaded)

    def test_schema_mismatch_rejected(self):
        self.slot.feature_version = 2
        with self.assertRaisesRegex(ValueError, 'schema mismatch'):
            SlotDetector(self.cfg)

    def test_duplicate_frames_removed(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in ('a.png', 'b.png'):
                cv2.imwrite(str(Path(tmp) / name), self.frame)
            self.assertEqual(len(load_images(Path(tmp))), 1)

    def test_augmentation_reproducible_and_preserves_source(self):
        before = self.frame.copy()
        a = augment_frame(self.frame, np.random.default_rng(42))
        b = augment_frame(self.frame, np.random.default_rng(42))
        np.testing.assert_array_equal(a, b)
        np.testing.assert_array_equal(self.frame, before)
        self.assertEqual(a.shape, self.frame.shape)
        self.assertEqual(a.dtype, np.uint8)

    def test_external_regression_image_excluded(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'external.png'
            cv2.imwrite(str(path), self.frame)
            self.assertEqual(load_images(Path(tmp), {path.resolve()}), [])

    def test_floor_changes_cannot_change_local_features(self):
        self.slot.inspection_polygon = [(15, 20), (45, 20), (40, 45), (20, 45)]
        self.slot.local_preprocessing = True
        self.slot.feature_version = 2
        self.slot.weights = [0.] * len(feature_names(2))
        det = SlotDetector(self.cfg)
        frame = self.frame.copy()
        cv2.circle(frame, (30, 30), 7, (240, 240, 240), -1)
        det.set_reference(frame)
        expected = det.features(frame)['test']
        changed = frame.copy()
        mask = det._masks['test'] > 0
        changed[~mask] = np.random.default_rng(42).integers(0, 256, (int((~mask).sum()), 3), dtype=np.uint8)
        np.testing.assert_array_equal(det.features(changed)['test'], expected)
        changed[27:34, 27:34] = 0
        self.assertFalse(np.array_equal(det.features(changed)['test'], expected))

    def test_inspection_mask_cannot_extend_beyond_slot(self):
        self.slot.inspection_polygon = [(0, 0), (63, 0), (63, 63), (0, 63)]
        det = SlotDetector(self.cfg)
        det._ensure_masks(self.frame.shape[:2])
        np.testing.assert_array_equal(det._masks['test'], polygon_mask(self.frame.shape[:2], self.slot.polygon))

    def test_inspection_settings_roundtrip(self):
        self.slot.inspection_polygon = [(15, 20), (45, 20), (45, 45), (15, 45)]
        self.slot.local_preprocessing = True
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'config.json'
            self.cfg.save(path)
            loaded = DetectorConfig.load(path)
            self.assertEqual(loaded.slots[0].inspection_polygon, [list(p) for p in self.slot.inspection_polygon])
            self.assertTrue(loaded.slots[0].local_preprocessing)


if __name__ == '__main__':
    unittest.main()
