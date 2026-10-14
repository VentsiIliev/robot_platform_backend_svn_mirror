"""Generate a reusable synthetic-workpiece dataset for Paint dry runs.

This script is intentionally configured through the constants below so it can
be launched directly with an IDE Run button.  It writes calibration-independent
normalized contours; runtime placement and orientation are applied later by the
Paint dry-run source.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
import random
import shutil
import sys
import tempfile

import cv2
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.engine.vision.implementation.VisionSystem.features.shape_matching_training.core.dataset.shape_factory import (  # noqa: E402
    ShapeFactory,
    ShapeType,
)


# ---------------------------------------------------------------------------
# IDE-editable generation settings
# ---------------------------------------------------------------------------

DATASET_ID = "standard-v1"
RANDOM_SEED = 25488
WORKPIECE_COUNT = 100

MIN_SIDE_MM = 50.0
MAX_SHORT_SIDE_MM = 200.0
# The active tray-dryer magazine has an approximately 221 x 214 mm usable
# envelope after the required placement margin. Keep both generated dimensions
# within 200 mm so every reusable item can be staged in that profile.
MAX_LONG_SIDE_MM = 200.0

SHAPE_TYPES = (
    ShapeType.RECTANGLE,
    ShapeType.ROUNDED_RECT,
    ShapeType.CIRCLE,
    ShapeType.ELLIPSE,
    ShapeType.EGG,
    ShapeType.TRIANGLE,
    ShapeType.PENTAGON,
    ShapeType.HEXAGON,
    ShapeType.T_SHAPE,
)

GENERATE_PREVIEWS = True
PREVIEW_SIZE_PX = 512
OVERWRITE_EXISTING_DATASET = False
OUTPUT_ROOT = PROJECT_ROOT / "src/robot_systems/paint/storage/dry_run_workpieces"


_SCHEMA_VERSION = 1
_REGULAR_SHAPES = {
    ShapeType.CIRCLE,
    ShapeType.SQUARE,
    ShapeType.TRIANGLE,
    ShapeType.DIAMOND,
    ShapeType.PENTAGON,
    ShapeType.HEXAGON,
    ShapeType.OCTAGON,
}


@dataclass(frozen=True)
class DatasetGenerationConfig:
    dataset_id: str
    random_seed: int
    workpiece_count: int
    min_side_mm: float
    max_short_side_mm: float
    max_long_side_mm: float
    shape_types: tuple[ShapeType, ...]
    output_root: Path
    generate_previews: bool = True
    preview_size_px: int = 512
    overwrite_existing_dataset: bool = False


@dataclass(frozen=True)
class GenerationResult:
    dataset_path: Path
    manifest_path: Path
    workpiece_count: int
    shape_distribution: dict[str, int]
    minimum_dimension_mm: float
    maximum_short_side_mm: float
    maximum_long_side_mm: float


def build_config() -> DatasetGenerationConfig:
    """Build a typed configuration from the editable constants above."""
    return DatasetGenerationConfig(
        dataset_id=DATASET_ID,
        random_seed=RANDOM_SEED,
        workpiece_count=WORKPIECE_COUNT,
        min_side_mm=MIN_SIDE_MM,
        max_short_side_mm=MAX_SHORT_SIDE_MM,
        max_long_side_mm=MAX_LONG_SIDE_MM,
        shape_types=tuple(SHAPE_TYPES),
        output_root=Path(OUTPUT_ROOT),
        generate_previews=GENERATE_PREVIEWS,
        preview_size_px=PREVIEW_SIZE_PX,
        overwrite_existing_dataset=OVERWRITE_EXISTING_DATASET,
    )


def generate_dataset(config: DatasetGenerationConfig) -> GenerationResult:
    """Generate, validate, and atomically publish one dry-run dataset."""
    _validate_config(config)
    destination = config.output_root / config.dataset_id
    config.output_root.mkdir(parents=True, exist_ok=True)
    if destination.exists() and not config.overwrite_existing_dataset:
        raise FileExistsError(
            f"Dataset already exists: {destination}. "
            "Set OVERWRITE_EXISTING_DATASET = True to replace it."
        )

    rng = random.Random(config.random_seed)
    staging = Path(tempfile.mkdtemp(prefix=f".{config.dataset_id}-", dir=config.output_root))
    try:
        preview_dir = staging / "previews"
        if config.generate_previews:
            preview_dir.mkdir(parents=True)

        items = []
        for index in range(config.workpiece_count):
            shape_type = config.shape_types[index % len(config.shape_types)]
            width_mm, height_mm = _choose_dimensions(shape_type, config, rng)
            item = _generate_item(index, shape_type, width_mm, height_mm)
            items.append(item)
            if config.generate_previews:
                _write_preview(item, preview_dir / f"{item['id']}.png", config.preview_size_px)

        manifest = {
            "schema_version": _SCHEMA_VERSION,
            "dataset_id": config.dataset_id,
            "random_seed": config.random_seed,
            "size_limits_mm": {
                "minimum_side": config.min_side_mm,
                "maximum_short_side": config.max_short_side_mm,
                "maximum_long_side": config.max_long_side_mm,
            },
            "placement": {
                "orientation": "assigned_at_runtime",
                "centroid": "assigned_at_runtime_inside_active_work_area",
            },
            "workpieces": items,
        }
        manifest_path = staging / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        _validate_manifest(manifest, config)

        if destination.exists():
            shutil.rmtree(destination)
        staging.rename(destination)
        staging = destination

        shape_distribution = dict(sorted(Counter(item["shape_type"] for item in items).items()))
        dimensions = [(float(item["width_mm"]), float(item["height_mm"])) for item in items]
        return GenerationResult(
            dataset_path=destination,
            manifest_path=destination / "manifest.json",
            workpiece_count=len(items),
            shape_distribution=shape_distribution,
            minimum_dimension_mm=min(min(width, height) for width, height in dimensions),
            maximum_short_side_mm=max(min(width, height) for width, height in dimensions),
            maximum_long_side_mm=max(max(width, height) for width, height in dimensions),
        )
    except Exception:
        if staging.exists() and staging != destination:
            shutil.rmtree(staging, ignore_errors=True)
        raise


def _validate_config(config: DatasetGenerationConfig) -> None:
    if not config.dataset_id or config.dataset_id in {".", ".."}:
        raise ValueError("DATASET_ID must be a nonempty folder name")
    if any(character in config.dataset_id for character in ("/", "\\", "\x00")):
        raise ValueError("DATASET_ID must not contain path separators")
    if config.workpiece_count <= 0:
        raise ValueError("WORKPIECE_COUNT must be positive")
    if not config.shape_types:
        raise ValueError("SHAPE_TYPES must contain at least one shape")
    unavailable = [shape for shape in config.shape_types if shape not in ShapeFactory.get_available_shapes()]
    if unavailable:
        raise ValueError(f"Unsupported SHAPE_TYPES: {unavailable}")
    if config.min_side_mm <= 0.0:
        raise ValueError("MIN_SIDE_MM must be positive")
    if config.max_short_side_mm < config.min_side_mm:
        raise ValueError("MAX_SHORT_SIDE_MM must be at least MIN_SIDE_MM")
    if config.max_long_side_mm < config.max_short_side_mm:
        raise ValueError("MAX_LONG_SIDE_MM must be at least MAX_SHORT_SIDE_MM")
    if config.preview_size_px < 128:
        raise ValueError("PREVIEW_SIZE_PX must be at least 128")


def _choose_dimensions(
    shape_type: ShapeType,
    config: DatasetGenerationConfig,
    rng: random.Random,
) -> tuple[float, float]:
    short_side = rng.uniform(config.min_side_mm, config.max_short_side_mm)
    if shape_type in _REGULAR_SHAPES:
        width_mm = height_mm = short_side
    else:
        long_side = rng.uniform(short_side, config.max_long_side_mm)
        width_mm, height_mm = (
            (long_side, short_side) if rng.random() < 0.5 else (short_side, long_side)
        )
    return round(width_mm, 3), round(height_mm, 3)


def _generate_item(
    index: int,
    shape_type: ShapeType,
    width_mm: float,
    height_mm: float,
) -> dict:
    raw = ShapeFactory.generate_shape(shape_type, scale=1.0, img_size=(512, 512))
    normalized = _normalize_contour(raw)
    item_id = f"{index + 1:04d}_{shape_type.value}_{_dimension_token(width_mm)}x{_dimension_token(height_mm)}"
    return {
        "id": item_id,
        "shape_type": shape_type.value,
        "width_mm": width_mm,
        "height_mm": height_mm,
        "contour_normalized": normalized.tolist(),
    }


def _normalize_contour(contour: np.ndarray) -> np.ndarray:
    points = np.asarray(contour, dtype=np.float64).reshape(-1, 2)
    if len(points) < 3:
        raise ValueError("Generated contour must contain at least three points")
    area = float(abs(cv2.contourArea(points.astype(np.float32))))
    if area <= 1e-9:
        raise ValueError("Generated contour has zero area")

    moments = cv2.moments(points.astype(np.float32))
    if abs(float(moments["m00"])) <= 1e-9:
        raise ValueError("Generated contour has no area centroid")
    centroid = np.array(
        [moments["m10"] / moments["m00"], moments["m01"] / moments["m00"]],
        dtype=np.float64,
    )
    if cv2.pointPolygonTest(points.astype(np.float32), tuple(centroid), False) < 0:
        raise ValueError("Generated contour centroid lies outside the workpiece")

    centered = points - centroid
    span = np.ptp(centered, axis=0)
    if np.any(span <= 1e-9):
        raise ValueError("Generated contour has a zero-width dimension")
    normalized = centered / span
    if not np.allclose(normalized[0], normalized[-1], atol=1e-9):
        normalized = np.vstack([normalized, normalized[0]])
    return np.round(normalized, decimals=8)


def _validate_manifest(manifest: dict, config: DatasetGenerationConfig) -> None:
    items = manifest.get("workpieces") or []
    if len(items) != config.workpiece_count:
        raise ValueError("Generated manifest contains the wrong number of workpieces")
    ids: set[str] = set()
    for item in items:
        item_id = str(item.get("id", ""))
        if not item_id or item_id in ids:
            raise ValueError(f"Invalid or duplicate workpiece ID: {item_id!r}")
        ids.add(item_id)
        width = float(item["width_mm"])
        height = float(item["height_mm"])
        short_side, long_side = sorted((width, height))
        if short_side < config.min_side_mm - 1e-6:
            raise ValueError(f"{item_id}: side is below the minimum")
        if short_side > config.max_short_side_mm + 1e-6:
            raise ValueError(f"{item_id}: short side exceeds the maximum")
        if long_side > config.max_long_side_mm + 1e-6:
            raise ValueError(f"{item_id}: long side exceeds the maximum")
        contour = np.asarray(item["contour_normalized"], dtype=np.float64)
        if contour.ndim != 2 or contour.shape[1] != 2 or len(contour) < 4:
            raise ValueError(f"{item_id}: normalized contour is invalid")
        if not np.all(np.isfinite(contour)):
            raise ValueError(f"{item_id}: contour contains non-finite coordinates")
        if not np.allclose(contour[0], contour[-1], atol=1e-9):
            raise ValueError(f"{item_id}: contour is not explicitly closed")
        if abs(float(cv2.contourArea(contour.astype(np.float32)))) <= 1e-9:
            raise ValueError(f"{item_id}: normalized contour has zero area")


def _write_preview(item: dict, path: Path, size_px: int) -> None:
    canvas = np.full((size_px, size_px, 3), 248, dtype=np.uint8)
    contour = np.asarray(item["contour_normalized"], dtype=np.float64)
    padding = max(24, size_px // 10)
    usable = size_px - 2 * padding
    minimum = np.min(contour, axis=0)
    span = np.ptp(contour, axis=0)
    points = (contour - minimum) / span * usable + padding
    polygon = np.rint(points).astype(np.int32).reshape(-1, 1, 2)
    cv2.fillPoly(canvas, [polygon], (222, 202, 232))
    cv2.polylines(canvas, [polygon], True, (144, 91, 169), 3, cv2.LINE_AA)
    normalized_center = (np.zeros(2, dtype=np.float64) - minimum) / span
    center_point = normalized_center * usable + padding
    center = tuple(np.rint(center_point).astype(np.int32))
    cv2.drawMarker(canvas, center, (30, 80, 210), cv2.MARKER_CROSS, 18, 2)
    label = f"{item['shape_type']}  {item['width_mm']:.1f} x {item['height_mm']:.1f} mm"
    cv2.putText(canvas, label, (12, size_px - 16), cv2.FONT_HERSHEY_SIMPLEX,
                0.55, (35, 35, 35), 1, cv2.LINE_AA)
    if not cv2.imwrite(str(path), canvas):
        raise OSError(f"Could not write preview: {path}")


def _dimension_token(value: float) -> str:
    return f"{value:.1f}".replace(".", "p")


def print_generation_summary(result: GenerationResult) -> None:
    print(f"Generated Paint dry-run dataset: {result.dataset_path}")
    print(f"Manifest: {result.manifest_path}")
    print(f"Workpieces: {result.workpiece_count}")
    print(f"Shapes: {result.shape_distribution}")
    print(
        "Dimensions: "
        f"minimum={result.minimum_dimension_mm:.3f} mm, "
        f"maximum short side={result.maximum_short_side_mm:.3f} mm, "
        f"maximum long side={result.maximum_long_side_mm:.3f} mm"
    )


def main() -> None:
    result = generate_dataset(build_config())
    print_generation_summary(result)


if __name__ == "__main__":
    main()
