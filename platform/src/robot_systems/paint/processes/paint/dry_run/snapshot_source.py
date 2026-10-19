from __future__ import annotations

import json
import logging
from pathlib import Path
import random
import time
from time import perf_counter

import cv2
import numpy as np

from src.engine.vision.i_capture_snapshot_service import VisionCaptureSnapshot

_logger = logging.getLogger(__name__)


class DryRunDatasetExhausted(RuntimeError):
    """The configured finite synthetic dataset has no item for this cycle."""


class PaintDryRunSnapshotSource:
    """Place reusable mm-sized contours inside the active capture area."""

    def __init__(
        self,
        *,
        manifest_path: str | Path,
        transformer_getter,
        work_area_service,
        image_size_getter,
        robot_service,
        work_area_id: str = "paint",
        margin_mm: float = 10.0,
        placement_attempts: int = 200,
    ) -> None:
        self._manifest_path = Path(manifest_path)
        self._transformer_getter = transformer_getter
        self._work_area_service = work_area_service
        self._image_size_getter = image_size_getter
        self._robot = robot_service
        self._work_area_id = str(work_area_id)
        self._margin_mm = max(0.0, float(margin_mm))
        self._placement_attempts = max(1, int(placement_attempts))
        self._manifest: dict | None = None
        self.last_metadata: dict | None = None
        self._next_dataset_index = 0
        self._run_start_index = 0

    def start_run(self) -> None:
        """Start a production run without rewinding the reusable dataset."""
        self._run_start_index = self._next_dataset_index
        _logger.info(
            "[DRY_RUN] Dataset run started at zero-based index=%d",
            self._run_start_index,
        )

    def capture_for_cycle(
        self,
        cycle_index: int,
        *,
        work_area_id: str | None = None,
        placement_key: str = "paint",
    ) -> VisionCaptureSnapshot:
        capture_started = perf_counter()
        manifest = self._get_manifest()
        items = manifest["workpieces"]
        index = self._run_start_index + max(1, int(cycle_index)) - 1
        if index >= len(items):
            raise DryRunDatasetExhausted("Dry-run dataset is exhausted")
        self._next_dataset_index = max(self._next_dataset_index, index + 1)
        item = items[index]
        width_px, height_px = self._image_size_getter()
        if width_px <= 0 or height_px <= 0:
            raise RuntimeError("Dry-run camera image size is unavailable")
        transformer = self._transformer_getter()
        if transformer is None or not transformer.is_available():
            raise RuntimeError("Dry-run mode requires an available camera calibration")

        active_work_area_id = str(work_area_id or self._work_area_id)
        normalized_boundary = self._work_area_service.get_work_area(active_work_area_id)
        if not normalized_boundary:
            raise RuntimeError(f"Dry-run work area '{active_work_area_id}' is not configured")
        boundary_px = np.asarray(
            [[float(x) * width_px, float(y) * height_px] for x, y in normalized_boundary],
            dtype=np.float64,
        )
        boundary_mm = np.asarray(
            [transformer.transform(float(x), float(y)) for x, y in boundary_px],
            dtype=np.float64,
        )
        fixed_center_mm = None
        if placement_key == "paint":
            center_px = _polygon_center(boundary_px)
            fixed_center_mm = np.asarray(
                transformer.transform(float(center_px[0]), float(center_px[1])),
                dtype=np.float64,
            )
        contour_mm, angle_deg, center_mm = self._place_item(
            item,
            boundary_mm,
            index,
            placement_key=placement_key,
            work_area_id=active_work_area_id,
            fixed_center_mm=fixed_center_mm,
        )
        placement_elapsed_s = perf_counter() - capture_started
        inverse_started = perf_counter()
        inverse_many = getattr(transformer, "inverse_transform_points", None)
        if callable(inverse_many):
            contour_pixels = inverse_many(contour_mm)
        else:
            contour_pixels = [
                transformer.inverse_transform(float(x), float(y))
                for x, y in contour_mm
            ]
        contour_px = np.asarray(contour_pixels, dtype=np.float32).reshape(-1, 1, 2)
        inverse_elapsed_s = perf_counter() - inverse_started
        frame = self._render_preview(width_px, height_px, boundary_px, contour_px, item, angle_deg)
        total_elapsed_s = perf_counter() - capture_started
        robot_pose = None
        if self._robot is not None:
            robot_pose = list(self._robot.get_current_position())
        _logger.warning(
            "[DRY_RUN] cycle=%d item=%s size_mm=(%.3f, %.3f) angle_deg=%.3f center_mm=(%.3f, %.3f)",
            cycle_index, item["id"], float(item["width_mm"]), float(item["height_mm"]),
            angle_deg, center_mm[0], center_mm[1],
        )
        _logger.info(
            "[DRY_RUN_CAPTURE_TIMING] cycle=%d item=%s points=%d "
            "placement_s=%.4f inverse_s=%.4f total_s=%.4f batch_inverse=%s",
            cycle_index,
            item["id"],
            len(contour_mm),
            placement_elapsed_s,
            inverse_elapsed_s,
            total_elapsed_s,
            callable(inverse_many),
        )
        self.last_metadata = {
            "dataset_manifest": str(self._manifest_path),
            "dataset_index": index,
            "workpiece": dict(item),
            "angle_deg": float(angle_deg),
            "center_mm": [float(center_mm[0]), float(center_mm[1])],
            "contour_mm": contour_mm.tolist(),
            "contour_px": contour_px.reshape(-1, 2).tolist(),
            "work_area_id": active_work_area_id,
            "placement_key": placement_key,
            "placement_mode": "work_area_center" if fixed_center_mm is not None else "random",
            "placement_margin_mm": self._margin_mm,
        }
        return VisionCaptureSnapshot(
            frame=frame,
            contours=[contour_px],
            robot_pose=robot_pose,
            timestamp_s=time.time(),
            source="paint_dry_run",
            work_area_id=active_work_area_id,
        )

    def _load_manifest(self) -> dict:
        try:
            payload = json.loads(self._manifest_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise RuntimeError(f"Could not load dry-run dataset: {self._manifest_path}") from exc
        items = payload.get("workpieces") if isinstance(payload, dict) else None
        if not isinstance(items, list) or not items:
            raise RuntimeError("Dry-run dataset contains no workpieces")
        return payload

    def _get_manifest(self) -> dict:
        if self._manifest is None:
            self._manifest = self._load_manifest()
        return self._manifest

    def _place_item(
        self,
        item: dict,
        boundary_mm: np.ndarray,
        index: int,
        *,
        placement_key: str,
        work_area_id: str,
        fixed_center_mm: np.ndarray | None = None,
    ):
        normalized = np.asarray(item["contour_normalized"], dtype=np.float64).reshape(-1, 2)
        local = normalized * np.array([float(item["width_mm"]), float(item["height_mm"])])
        placement_salt = sum(
            (position + 1) * ord(character)
            for position, character in enumerate(str(placement_key))
        )
        seed = (
            int(self._get_manifest().get("random_seed", 0))
            + index * 1_000_003
            + placement_salt * 10_007
        )
        rng = random.Random(seed)
        minimum = np.min(boundary_mm, axis=0)
        maximum = np.max(boundary_mm, axis=0)
        polygon = boundary_mm.astype(np.float32).reshape(-1, 1, 2)
        for _attempt in range(self._placement_attempts):
            # Retry orientation as well as position. A long workpiece can be
            # valid in the area but impossible at one particular angle.
            angle_deg = rng.uniform(0.0, 360.0)
            angle = np.deg2rad(angle_deg)
            rotation = np.array([
                [np.cos(angle), -np.sin(angle)],
                [np.sin(angle), np.cos(angle)],
            ])
            rotated = local @ rotation.T
            rotated_minimum = np.min(rotated, axis=0)
            rotated_maximum = np.max(rotated, axis=0)
            if fixed_center_mm is None:
                center_minimum = minimum + self._margin_mm - rotated_minimum
                center_maximum = maximum - self._margin_mm - rotated_maximum
                if np.any(center_minimum > center_maximum):
                    continue
                center = np.array([
                    rng.uniform(float(center_minimum[0]), float(center_maximum[0])),
                    rng.uniform(float(center_minimum[1]), float(center_maximum[1])),
                ])
            else:
                center = np.asarray(fixed_center_mm, dtype=np.float64).reshape(2)
            placed = rotated + center
            if self._footprint_is_inside(polygon, placed):
                return placed, angle_deg, center
        raise RuntimeError(
            f"Dry-run workpiece '{item['id']}' does not fit inside work area "
            f"'{work_area_id}' with {self._margin_mm:.1f} mm margin"
        )

    def _footprint_is_inside(self, boundary, contour: np.ndarray) -> bool:
        """Require the complete polygon footprint and clearance inside the area."""
        workpiece = np.asarray(contour, dtype=np.float64).reshape(-1, 2)
        area = np.asarray(boundary, dtype=np.float64).reshape(-1, 2)
        if len(workpiece) < 3 or len(area) < 3:
            return False
        area_cv = area.astype(np.float32).reshape(-1, 1, 2)
        for point in workpiece:
            if cv2.pointPolygonTest(
                area_cv, (float(point[0]), float(point[1])), True
            ) < self._margin_mm:
                return False

        # In a concave area, an edge can bridge a notch although both of its
        # endpoints are inside. Exact edge separation closes that gap.
        workpiece_closed = np.vstack([workpiece, workpiece[0]])
        area_closed = np.vstack([area, area[0]])
        for workpiece_start, workpiece_end in zip(
            workpiece_closed[:-1], workpiece_closed[1:]
        ):
            for area_start, area_end in zip(area_closed[:-1], area_closed[1:]):
                if _segment_distance(
                    workpiece_start, workpiece_end, area_start, area_end
                ) <= self._margin_mm:
                    return False
        return True

    @staticmethod
    def _render_preview(width, height, boundary_px, contour_px, item, angle_deg):
        frame = np.full((int(height), int(width), 3), 245, dtype=np.uint8)
        boundary = np.rint(boundary_px).astype(np.int32).reshape(-1, 1, 2)
        contour = np.rint(contour_px).astype(np.int32)
        cv2.polylines(frame, [boundary], True, (120, 120, 120), 2, cv2.LINE_AA)
        cv2.fillPoly(frame, [contour], (222, 202, 232))
        cv2.polylines(frame, [contour], True, (144, 91, 169), 3, cv2.LINE_AA)
        moments = cv2.moments(contour)
        if moments["m00"]:
            center = (int(moments["m10"] / moments["m00"]), int(moments["m01"] / moments["m00"]))
            cv2.drawMarker(frame, center, (30, 80, 210), cv2.MARKER_CROSS, 22, 2)
        cv2.putText(
            frame, f"DRY RUN  {item['id']}  angle={angle_deg:.1f} deg", (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (30, 30, 180), 2, cv2.LINE_AA,
        )
        return frame


def _polygon_center(points: np.ndarray) -> tuple[float, float]:
    """Match the magazine-release work-area centroid calculation."""
    area = np.asarray(points, dtype=np.float64).reshape(-1, 2)
    if len(area) < 3:
        raise RuntimeError("Dry-run work area requires at least three points")
    contour = area.astype(np.float32).reshape(-1, 1, 2)
    moments = cv2.moments(contour)
    if abs(float(moments.get("m00", 0.0))) > 1e-9:
        return (
            float(moments["m10"] / moments["m00"]),
            float(moments["m01"] / moments["m00"]),
        )
    return float(np.mean(area[:, 0])), float(np.mean(area[:, 1]))


def _segment_distance(a: np.ndarray, b: np.ndarray, c: np.ndarray, d: np.ndarray) -> float:
    """Return the planar minimum distance between two closed segments."""
    if _segments_intersect(a, b, c, d):
        return 0.0
    return min(
        _point_segment_distance(a, c, d),
        _point_segment_distance(b, c, d),
        _point_segment_distance(c, a, b),
        _point_segment_distance(d, a, b),
    )


def _segments_intersect(a, b, c, d, *, tolerance: float = 1e-9) -> bool:
    def orientation(p, q, r) -> float:
        first = q - p
        second = r - p
        return float(first[0] * second[1] - first[1] * second[0])

    def on_segment(p, q, r) -> bool:
        return bool(
            min(p[0], r[0]) - tolerance <= q[0] <= max(p[0], r[0]) + tolerance
            and min(p[1], r[1]) - tolerance <= q[1] <= max(p[1], r[1]) + tolerance
        )

    o1, o2 = orientation(a, b, c), orientation(a, b, d)
    o3, o4 = orientation(c, d, a), orientation(c, d, b)
    if ((o1 > tolerance and o2 < -tolerance) or (o1 < -tolerance and o2 > tolerance)) and (
        (o3 > tolerance and o4 < -tolerance) or (o3 < -tolerance and o4 > tolerance)
    ):
        return True
    return bool(
        (abs(o1) <= tolerance and on_segment(a, c, b))
        or (abs(o2) <= tolerance and on_segment(a, d, b))
        or (abs(o3) <= tolerance and on_segment(c, a, d))
        or (abs(o4) <= tolerance and on_segment(c, b, d))
    )


def _point_segment_distance(point, start, end) -> float:
    segment = end - start
    length_squared = float(np.dot(segment, segment))
    if length_squared <= 1e-18:
        return float(np.linalg.norm(point - start))
    fraction = float(np.dot(point - start, segment) / length_squared)
    projection = start + min(1.0, max(0.0, fraction)) * segment
    return float(np.linalg.norm(point - projection))
