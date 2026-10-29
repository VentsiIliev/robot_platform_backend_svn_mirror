"""Development-only expected/detected pose overlays."""

import cv2
import numpy as np

from ..configuration import DetectorConfiguration
from ..models import DetectionResult, HeadStatus, Image
from .settings import Color, ViewSettings


def dashed_box(
    image: Image, rect: tuple[int, int, int, int], color: Color, view: ViewSettings
) -> None:
    x, y, w, h = rect
    xs, ys = np.arange(x, x + w, view.dash_period), np.arange(y, y + h, view.dash_period)
    horizontal = np.stack(
        (
            np.column_stack((xs, np.full_like(xs, y))),
            np.column_stack((np.minimum(xs + view.dash_length, x + w), np.full_like(xs, y))),
        ),
        axis=1,
    )
    vertical = np.stack(
        (
            np.column_stack((np.full_like(ys, x), ys)),
            np.column_stack((np.full_like(ys, x), np.minimum(ys + view.dash_length, y + h))),
        ),
        axis=1,
    )
    segments = np.concatenate((horizontal, horizontal + [0, h], vertical, vertical + [w, 0]))
    cv2.polylines(image, list(segments.astype(np.int32)), False, color, 1, cv2.LINE_AA)


class OverlayRenderer:
    def __init__(self, configuration: DetectorConfiguration, view: ViewSettings) -> None:
        self._calibration = configuration.calibration
        self._alignment = configuration.alignment
        self._view = view
        self._ignored_rectangles = tuple(r.coordinates for r in self._calibration.ignored_regions)

    def draw(self, frame: Image, result: DetectionResult, *, fps: float | None = None) -> Image:
        out = frame.copy()
        state = result.status
        colors = {
            HeadStatus.HEAD_PRESENT: self._view.present_color,
            HeadStatus.HEAD_MISALIGNED: self._view.misaligned_color,
            HeadStatus.HEAD_MISSING: self._view.missing_color,
            HeadStatus.UNKNOWN: self._view.unknown_color,
        }
        color = colors[state]
        x, y, w, h = self._calibration.inspection_region.coordinates
        cv2.rectangle(out, (x, y), (x + w, y + h), color, 2)
        for ix, iy, iw, ih in self._ignored_rectangles:
            cv2.rectangle(out, (ix, iy), (ix + iw, iy + ih), self._view.ignored_color, 1)
            cv2.putText(
                out,
                "IGNORED",
                (ix + 3, iy + 15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                self._view.ignored_color,
                1,
            )
        cv2.putText(out, state.value, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.85, color, 2)
        if fps is not None:
            cv2.putText(
                out, f"FPS: {fps:.1f}", (330, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2
            )
        if self._view.show_expected:
            expected_color = self._view.expected_color
            cv2.putText(
                out,
                "Expected: cyan dashed | Detected: solid",
                (20, 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                expected_color,
                1,
            )
            reference_points = []
            observed_points = []
            for match in result.diagnostics.present.matches:
                feature = match.feature
                rect = feature.region.coordinates
                dashed_box(out, rect, expected_color, self._view)
                expected_center = np.rint(
                    [
                        feature.region.x + feature.region.width / 2,
                        feature.region.y + feature.region.height / 2,
                    ]
                ).astype(int)
                cv2.drawMarker(out, tuple(expected_center), expected_color, cv2.MARKER_CROSS, 9, 1)
                if feature.orientation_invariant:
                    reference_points.append(expected_center)
                    if match.passed and match.center is not None:
                        observed_points.append(np.rint(match.center).astype(int))
                if (
                    match.passed
                    and match.center is not None
                    and np.linalg.norm(np.asarray(match.center) - expected_center) > 3
                ):
                    cv2.arrowedLine(
                        out,
                        tuple(expected_center),
                        tuple(np.rint(match.center).astype(int)),
                        color,
                        1,
                        cv2.LINE_AA,
                        tipLength=0.15,
                    )
            if len(reference_points) >= 2:
                cv2.polylines(out, [np.array(reference_points, np.int32)], False, expected_color, 1)
            if len(observed_points) >= 2:
                cv2.polylines(out, [np.array(observed_points, np.int32)], False, color, 2)
        line = 95 if self._view.show_expected else 75
        if result.diagnostics.quality.issue:
            cv2.putText(out, result.message, (20, line), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            line += 25
        for match in result.diagnostics.present.matches:
            f = match.feature
            mx, my = match.position
            box_color = (0, 220, 0) if match.passed else (0, 0, 255)
            cv2.rectangle(
                out, (mx, my), (mx + int(f.region.width), my + int(f.region.height)), box_color, 2
            )
            dx, dy = match.shift
            cv2.putText(
                out,
                f"{f.name}: {match.score:.3f} shift=({dx:+d},{dy:+d})",
                (20, line),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                box_color,
                2,
            )
            line += 25
        for match in result.diagnostics.missing.matches:
            f = match.feature
            mx, my = match.position
            box_color = (255, 200, 0) if match.passed else (110, 110, 110)
            cv2.rectangle(
                out, (mx, my), (mx + int(f.region.width), my + int(f.region.height)), box_color, 1
            )
            cv2.putText(
                out,
                f"missing/{f.name}: {match.score:.3f}",
                (20, line),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                box_color,
                2,
            )
            line += 25
        geom = "OK" if result.diagnostics.present.verified else "N/A"
        cv2.putText(
            out,
            f"Plate: {result.diagnostics.missing.plate_similarity:.3f} | Geometry: {geom} | Missing bolts: {result.diagnostics.missing.landmark_count}",
            (20, line),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            2,
        )
        line += 25
        cv2.putText(
            out,
            f"Consensus: {result.diagnostics.present.inlier_count}/{len(self._calibration.present_features)} | Rotation: {result.diagnostics.pose.rotation_degrees:+.1f} deg | Offset: ({result.diagnostics.pose.offset[0]:+.0f}, {result.diagnostics.pose.offset[1]:+.0f})",
            (20, line),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            2,
        )
        line += 25
        alignment = result.alignment
        placement = (
            "RECHECKING"
            if result.held_warning
            else "N/A"
            if alignment is None
            else "OK"
            if alignment.aligned
            else "MISALIGNED"
        )
        cv2.putText(
            out,
            f"Placement: {placement} | Limits: {self._alignment.max_translation_pixels:g} px, {self._alignment.max_rotation_degrees:g} deg",
            (20, line),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            2,
        )
        if result.held_warning:
            cv2.putText(
                out,
                "Rechecking head position",
                (20, line + 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2,
            )
        return out
