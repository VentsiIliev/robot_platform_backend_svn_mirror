import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest


_SCRIPT_PATH = (
    Path(__file__).resolve().parents[3]
    / "src/robot_systems/paint/scripts/generate_dry_run_dataset.py"
)
_SPEC = importlib.util.spec_from_file_location("paint_generate_dry_run_dataset", _SCRIPT_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"Could not load Paint dry-run generator: {_SCRIPT_PATH}")
_MODULE = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _MODULE
_SPEC.loader.exec_module(_MODULE)

DatasetGenerationConfig = _MODULE.DatasetGenerationConfig
ShapeType = _MODULE.ShapeType
generate_dataset = _MODULE.generate_dataset


class GeneratePaintDryRunDatasetTests(unittest.TestCase):
    def _config(self, output_root: Path, seed: int = 42) -> DatasetGenerationConfig:
        return DatasetGenerationConfig(
            dataset_id="test-v1",
            random_seed=seed,
            workpiece_count=18,
            min_side_mm=50.0,
            max_short_side_mm=200.0,
            max_long_side_mm=300.0,
            shape_types=(
                ShapeType.RECTANGLE,
                ShapeType.CIRCLE,
                ShapeType.ELLIPSE,
                ShapeType.EGG,
                ShapeType.TRIANGLE,
                ShapeType.ROUNDED_RECT,
                ShapeType.T_SHAPE,
            ),
            output_root=output_root,
            generate_previews=False,
        )

    def test_generates_closed_normalized_contours_with_valid_physical_sizes(self):
        with tempfile.TemporaryDirectory() as directory:
            result = generate_dataset(self._config(Path(directory)))
            manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))

            self.assertEqual(len(manifest["workpieces"]), 18)
            self.assertIn("egg", {item["shape_type"] for item in manifest["workpieces"]})
            for item in manifest["workpieces"]:
                width = float(item["width_mm"])
                height = float(item["height_mm"])
                self.assertGreaterEqual(min(width, height), 50.0)
                self.assertLessEqual(min(width, height), 200.0)
                self.assertLessEqual(max(width, height), 300.0)
                self.assertEqual(
                    item["contour_normalized"][0],
                    item["contour_normalized"][-1],
                )

    def test_same_seed_produces_identical_manifest(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            first_result = generate_dataset(self._config(Path(first), seed=25488))
            second_result = generate_dataset(self._config(Path(second), seed=25488))

            self.assertEqual(
                first_result.manifest_path.read_text(encoding="utf-8"),
                second_result.manifest_path.read_text(encoding="utf-8"),
            )

    def test_refuses_to_overwrite_existing_dataset(self):
        with tempfile.TemporaryDirectory() as directory:
            config = self._config(Path(directory))
            generate_dataset(config)

            with self.assertRaises(FileExistsError):
                generate_dataset(config)


if __name__ == "__main__":
    unittest.main()
