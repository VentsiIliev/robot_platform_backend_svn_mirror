import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

import numpy as np


_ROOT = Path(__file__).resolve().parents[3]
_PATH = _ROOT / "src/robot_systems/paint/diagnostics/failure_bundle.py"
_SPEC = importlib.util.spec_from_file_location("paint_failure_bundle_tested", _PATH)
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)


class PaintFailureBundleTests(unittest.TestCase):
    def test_writes_reproduction_data_motion_profiles_and_capture(self):
        failure = SimpleNamespace(code="motion", stage="paint", message="rejected")
        snapshot = SimpleNamespace(
            source="paint_dry_run",
            timestamp_s=123.0,
            work_area_id="paint",
            robot_pose=[1, 2, 3, 4, 5, 6],
            contours=[np.asarray([[[10, 20]], [[30, 40]]], dtype=np.float32)],
            frame=np.zeros((20, 30, 3), dtype=np.uint8),
        )
        context = SimpleNamespace(
            cycle_index=7,
            diagnostic_cycle_id="abc123",
            operation_failure=failure,
            tray_failure=None,
            raw_process_config={"acceleration_scaling_percent": 50},
            process_config={"pickup": {"velocity": 25, "acceleration": 10}},
            dry_run_metadata={"angle_deg": 42.0, "center_mm": [100, 200]},
            snapshot=snapshot,
            workpiece_description="egg",
            raw_workpiece={"id": "egg-1"},
            contour=np.asarray([[10, 20], [30, 40]]),
            execution_plan={"paint_trajectory": [[1, 2, 3, 4, 5, 6]]},
            state_timing_recorder={"paint": 1.25},
            paint_timing_recorder=None,
            paint_timing_session=None,
            total_started_at=1.0,
            paint_started_at=2.0,
            snapshot_dict=lambda: {"outcome": "failed", "cycle_index": 7},
        )
        executor = SimpleNamespace(
            _last_pickup_plan={"pickup": [1, 2, 3, 4, 5, 6]},
            _cycle_dropoff_strategy="plate_layout",
            _pending_stage_pose=[6, 5, 4, 3, 2, 1],
            _last_process_end_pose=None,
            _last_prepositioned_start_group=None,
            diagnostic_motion_commands=[{
                "kind": "single_move", "label": "pickup", "vel": 25.0,
                "acc": 10.0, "position": [1, 2, 3, 4, 5, 6],
            }],
            _motion=SimpleNamespace(last_motion_error="backend rejected move"),
            _last_safe_travel_error="",
            _last_pickup_contact_mode="sensor_controlled_fast_lin",
        )

        with tempfile.TemporaryDirectory() as directory:
            result = _MODULE.write_paint_failure_bundle(context, executor, directory)
            self.assertIsNotNone(result)
            self.assertTrue((result / "capture.png").is_file())
            payload = json.loads((result / "failure_bundle.json").read_text(encoding="utf-8"))

        self.assertEqual(payload["cycle_id"], "abc123")
        self.assertEqual(payload["motion"]["commands"][0]["vel"], 25.0)
        self.assertEqual(payload["motion"]["commands"][0]["acc"], 10.0)
        self.assertEqual(payload["dry_run_placement"]["angle_deg"], 42.0)
        self.assertEqual(payload["effective_process_config"]["pickup"]["acceleration"], 10)

    def test_storage_failure_does_not_raise(self):
        context = SimpleNamespace(cycle_index=1, diagnostic_cycle_id="x")
        self.assertIsNone(
            _MODULE.write_paint_failure_bundle(context, object(), "/dev/null/not-a-directory")
        )


if __name__ == "__main__":
    unittest.main()
