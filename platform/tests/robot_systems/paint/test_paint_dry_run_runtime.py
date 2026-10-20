import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np


_ROOT = Path(__file__).resolve().parents[3]


def _load(name: str, relative_path: str):
    path = _ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_source_module = _load(
    "paint_dry_run_snapshot_source_tested",
    "src/robot_systems/paint/processes/paint/dry_run/snapshot_source.py",
)
_condition_module = _load(
    "paint_dry_run_minimum_z_condition_tested",
    "src/robot_systems/paint/processes/paint/dry_run/minimum_z_condition.py",
)

PaintDryRunSnapshotSource = _source_module.PaintDryRunSnapshotSource
DryRunDatasetExhausted = _source_module.DryRunDatasetExhausted
DryRunMinimumZPickupCondition = _condition_module.DryRunMinimumZPickupCondition


class _IdentityTransformer:
    def __init__(self):
        self.batch_inverse_calls = 0

    def is_available(self):
        return True

    def transform(self, x, y):
        return float(x), float(y)

    def inverse_transform(self, x, y):
        return float(x), float(y)

    def inverse_transform_points(self, points):
        self.batch_inverse_calls += 1
        return np.asarray(points, dtype=float)


class _WorkArea:
    def get_work_area(self, area_id):
        assert area_id in {"paint", "magazine"}
        return [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]


class _Robot:
    def __init__(self, pose=None):
        self.pose = list(pose or [0.0, 0.0, 100.0, 0.0, 0.0, 0.0])

    def get_current_position(self):
        return list(self.pose)


class PaintDryRunRuntimeTests(unittest.TestCase):
    def test_fits_same_item_to_all_enabled_areas_and_usable_tray(self):
        from src.robot_systems.paint.processes.paint.configuration.models import (
            DropoffStrategy, PaintDropoffConfig, PaintMagazineLoadConfig, PaintProcessConfig,
        )

        class WorkAreas:
            def get_work_area(self, area_id):
                side = 0.3 if area_id == "paint" else 0.2
                return [(0, 0), (side, 0), (side, side), (0, side)]

        config = PaintProcessConfig(
            magazine_load=PaintMagazineLoadConfig(enabled=True),
            dropoff=PaintDropoffConfig(
                strategy=DropoffStrategy.PLATE_LAYOUT,
                plate_corners=[[0, 0, 10, 180, 0, 0], [160, 0, 10, 180, 0, 0],
                               [160, 300, 10, 180, 0, 0], [0, 300, 10, 180, 0, 0]],
                plate_margin_left_mm=10, plate_margin_right_mm=10,
            ),
        )
        with tempfile.TemporaryDirectory() as directory:
            source = PaintDryRunSnapshotSource(
                manifest_path=self._manifest(Path(directory)),
                transformer_getter=lambda: _IdentityTransformer(),
                work_area_service=WorkAreas(), image_size_getter=lambda: (1000, 1000),
                robot_service=_Robot(), process_config_getter=lambda: config,
            )
            original = source._get_manifest()["workpieces"][0].copy()
            magazine = source.capture_for_cycle(1, placement_key="magazine", work_area_id="magazine")
            magazine_item = source.last_metadata["workpiece"].copy()
            paint = source.capture_for_cycle(1)
            self.assertEqual(magazine_item, source.last_metadata["workpiece"])
            self.assertLess(source.last_metadata["fit_scale"], 1.0)
            self.assertEqual(original, source._get_manifest()["workpieces"][0])
            for snapshot in (magazine, paint):
                side = 200 if snapshot.work_area_id == "magazine" else 300
                boundary = np.array([[0, 0], [side, 0], [side, side], [0, side]])
                self.assertTrue(source._footprint_is_inside(boundary, snapshot.contours[0]))
            fitted = source.last_metadata["workpiece"]
            local = np.asarray(fitted["contour_normalized"]) * [fitted["width_mm"], fitted["height_mm"]]
            self.assertLessEqual(2 * np.linalg.norm(local, axis=1).max(), 130.0 + 1e-6)

    def test_synthetic_workpiece_is_scaled_to_small_capture_area(self):
        with tempfile.TemporaryDirectory() as directory:
            source = PaintDryRunSnapshotSource(
                manifest_path=self._manifest(Path(directory)),
                transformer_getter=lambda: _IdentityTransformer(),
                work_area_service=_WorkArea(), image_size_getter=lambda: (100, 100),
                robot_service=_Robot(),
            )
            snapshot = source.capture_for_cycle(1)
            points = snapshot.contours[0].reshape(-1, 2)
            self.assertTrue(np.all(points >= 15.0 - 1e-5))
            self.assertTrue(np.all(points <= 85.0 + 1e-5))
            self.assertLess(source.last_metadata["fit_scale"], 1.0)

    def test_rejects_work_area_without_margin_clearance_before_rendering(self):
        with tempfile.TemporaryDirectory() as directory:
            source = PaintDryRunSnapshotSource(
                manifest_path=self._manifest(Path(directory)),
                transformer_getter=lambda: _IdentityTransformer(),
                work_area_service=_WorkArea(), image_size_getter=lambda: (20, 20),
                robot_service=_Robot(),
            )
            with self.assertRaisesRegex(RuntimeError, "no usable area"):
                source.capture_for_cycle(1)
            self.assertIsNone(source.last_metadata)

    def _manifest(self, root: Path) -> Path:
        path = root / "manifest.json"
        path.write_text(json.dumps({
            "schema_version": 1,
            "dataset_id": "test-v1",
            "random_seed": 123,
            "workpieces": [
                {
                    "id": "rectangle",
                    "shape_type": "rectangle",
                    "width_mm": 200.0,
                    "height_mm": 100.0,
                    "contour_normalized": [
                        [-0.5, -0.5], [0.5, -0.5],
                        [0.5, 0.5], [-0.5, 0.5], [-0.5, -0.5],
                    ],
                },
                {
                    "id": "egg",
                    "shape_type": "egg",
                    "width_mm": 120.0,
                    "height_mm": 180.0,
                    "contour_normalized": [
                        [0.0, -0.5], [0.5, 0.1], [0.0, 0.5],
                        [-0.5, 0.1], [0.0, -0.5],
                    ],
                },
            ],
        }), encoding="utf-8")
        return path

    def test_source_places_rotated_contours_inside_work_area_and_exhausts(self):
        with tempfile.TemporaryDirectory() as directory:
            source = PaintDryRunSnapshotSource(
                manifest_path=self._manifest(Path(directory)),
                transformer_getter=lambda: _IdentityTransformer(),
                work_area_service=_WorkArea(),
                image_size_getter=lambda: (1000, 1000),
                robot_service=_Robot(),
                margin_mm=10.0,
            )

            first = source.capture_for_cycle(1)
            first_center = list(source.last_metadata["center_mm"])
            second = source.capture_for_cycle(2)
            second_center = list(source.last_metadata["center_mm"])
            self.assertEqual(first.source, "paint_dry_run")
            self.assertFalse(np.array_equal(first.contours[0], second.contours[0]))
            self.assertEqual([500.0, 500.0], first_center)
            self.assertEqual([500.0, 500.0], second_center)
            self.assertEqual("work_area_center", source.last_metadata["placement_mode"])
            for snapshot in (first, second):
                points = np.asarray(snapshot.contours[0]).reshape(-1, 2)
                self.assertTrue(np.all(points >= 10.0))
                self.assertTrue(np.all(points <= 990.0))
            with self.assertRaises(DryRunDatasetExhausted):
                source.capture_for_cycle(3)

            magazine = source.capture_for_cycle(
                1, work_area_id="magazine", placement_key="magazine"
            )
            self.assertEqual("magazine", magazine.work_area_id)
            self.assertEqual("magazine", source.last_metadata["placement_key"])
            self.assertEqual("random", source.last_metadata["placement_mode"])

    def test_minimum_z_condition_latches_until_rearmed(self):
        robot = _Robot([0, 0, 50, 0, 0, 0])
        condition = DryRunMinimumZPickupCondition(robot, minimum_z_mm=10.0)
        self.assertFalse(condition.is_active())
        robot.pose[2] = 10.0
        self.assertTrue(condition.is_active())
        robot.pose[2] = 50.0
        self.assertTrue(condition.is_active())
        condition.on_servo_start()
        self.assertFalse(condition.is_active())

    def test_new_run_continues_from_next_dataset_item(self):
        with tempfile.TemporaryDirectory() as directory:
            source = PaintDryRunSnapshotSource(
                manifest_path=self._manifest(Path(directory)),
                transformer_getter=lambda: _IdentityTransformer(),
                work_area_service=_WorkArea(),
                image_size_getter=lambda: (1000, 1000),
                robot_service=_Robot(),
                margin_mm=10.0,
            )

            source.start_run()
            source.capture_for_cycle(1, placement_key="magazine")
            self.assertEqual("rectangle", source.last_metadata["workpiece"]["id"])
            source.capture_for_cycle(1, placement_key="paint")
            self.assertEqual("rectangle", source.last_metadata["workpiece"]["id"])

            source.start_run()
            source.capture_for_cycle(1, placement_key="magazine")
            self.assertEqual("egg", source.last_metadata["workpiece"]["id"])

    def test_capture_uses_batch_inverse_for_dense_contour(self):
        with tempfile.TemporaryDirectory() as directory:
            transformer = _IdentityTransformer()
            source = PaintDryRunSnapshotSource(
                manifest_path=self._manifest(Path(directory)),
                transformer_getter=lambda: transformer,
                work_area_service=_WorkArea(),
                image_size_getter=lambda: (1000, 1000),
                robot_service=_Robot(),
                margin_mm=10.0,
            )

            source.capture_for_cycle(2)

            self.assertEqual(1, transformer.batch_inverse_calls)

    def test_full_footprint_cannot_bridge_a_concave_work_area_notch(self):
        with tempfile.TemporaryDirectory() as directory:
            source = PaintDryRunSnapshotSource(
                manifest_path=self._manifest(Path(directory)),
                transformer_getter=lambda: _IdentityTransformer(),
                work_area_service=_WorkArea(),
                image_size_getter=lambda: (1000, 1000),
                robot_service=_Robot(),
                margin_mm=0.0,
            )
            concave_area = np.asarray([
                [0, 0], [100, 0], [100, 100], [60, 100],
                [60, 40], [40, 40], [40, 100], [0, 100],
            ], dtype=np.float32).reshape(-1, 1, 2)
            bridges_notch = np.asarray([
                [30, 50], [70, 50], [70, 80], [30, 80],
            ], dtype=np.float64)

            self.assertFalse(
                source._footprint_is_inside(concave_area, bridges_notch)
            )

    def test_placement_retries_orientation_for_long_workpiece(self):
        with tempfile.TemporaryDirectory() as directory:
            source = PaintDryRunSnapshotSource(
                manifest_path=self._manifest(Path(directory)),
                transformer_getter=lambda: _IdentityTransformer(),
                work_area_service=_WorkArea(),
                image_size_getter=lambda: (1000, 1000),
                robot_service=_Robot(),
                margin_mm=10.0,
                placement_attempts=200,
            )
            item = {
                "id": "long",
                "width_mm": 145.0,
                "height_mm": 299.0,
                "contour_normalized": [
                    [-0.5, -0.5], [0.5, -0.5],
                    [0.5, 0.5], [-0.5, 0.5], [-0.5, -0.5],
                ],
            }
            narrow_area = np.asarray([
                [0, 0], [340, 0], [340, 190], [0, 190],
            ], dtype=np.float64)

            placed, _angle, _center = source._place_item(
                item,
                narrow_area,
                1,
                placement_key="magazine",
                work_area_id="magazine",
            )

            self.assertTrue(
                source._footprint_is_inside(
                    narrow_area.astype(np.float32).reshape(-1, 1, 2), placed
                )
            )


if __name__ == "__main__":
    unittest.main()
