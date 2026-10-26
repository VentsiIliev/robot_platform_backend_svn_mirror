from datetime import datetime, timezone
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

import cv2
import numpy as np

from src.engine.vision.i_vision_service import IVisionService
from .i_image_capture_service import CapturedImage, IImageCaptureService
from ..processing.capture_decomposition import decompose_capture
from ..processing.robot_decomposition import build_robot_result
from ..processing.sampled_path import build_sampled_result


class ImageCaptureApplicationService(IImageCaptureService):
    def __init__(self, vision_service: IVisionService | None, output_directory: str,
                 robot_converter=None, work_area_getter=None, contour_sampler=None):
        self._vision = vision_service
        self._directory = Path(output_directory)
        self._contour_sampler = contour_sampler
        self._robot_converter = robot_converter
        self._work_area_getter = work_area_getter

    def output_directory(self) -> str:
        return str(self._directory)

    def capture(self) -> CapturedImage:
        if self._vision is None:
            raise RuntimeError("Vision service is unavailable.")
        area = self._work_area_getter() if self._work_area_getter else ""
        frame = self._vision.capture_corrected_image()
        if frame is None or frame.size == 0:
            raise RuntimeError("No camera image is available.")
        captured_at = datetime.now(timezone.utc).isoformat()
        # Detection receives a copy so even an adapter that draws cannot alter
        # the image we save. Never query live contours from a different frame.
        found = self._vision.detect_contours_for_image(frame.copy())
        contours = tuple(
            tuple((float(x), float(y)) for x, y in np.asarray(contour).reshape(-1, 2))
            for contour in found
        )
        preview = frame.copy()
        if contours:
            cv2.drawContours(preview, [np.asarray(c, dtype=np.int32).reshape(-1, 1, 2)
                                      for c in contours], -1, (0, 255, 0), 2)
        decomposition, overlay, counts = decompose_capture(frame, contours)
        robot_result = robot_preview = None
        sampled_result = sampled_preview = None
        if self._robot_converter is not None:
            if not area or area != self._work_area_getter():
                raise RuntimeError("Work area changed during capture. Capture again.")
            robot_result, robot_plot = build_robot_result(contours, self._robot_converter, area)
            robot_preview = self._encode(robot_plot)
            if self._contour_sampler is not None:
                sampled_result, sampled_plot = build_sampled_result(json.loads(robot_result), self._contour_sampler)
                sampled_preview = self._encode(sampled_plot)
            if area != self._work_area_getter():
                raise RuntimeError("Work area changed during capture. Capture again.")
        return CapturedImage(
            image=self._encode(frame), preview=self._encode(preview),
            contours=contours, width=int(frame.shape[1]), height=int(frame.shape[0]),
            captured_at=captured_at,
            decomposition=decomposition, decomposition_preview=self._encode(overlay),
            line_count=counts["lines"], arc_count=counts["arcs"],
            exceeds_tolerance=counts["exceeds_tolerance"], failed_contours=counts["failed_contours"],
            robot_result=robot_result, robot_preview=robot_preview,
            sampled_result=sampled_result, sampled_preview=sampled_preview,
        )

    @staticmethod
    def _encode(frame) -> bytes:
        ok, encoded = cv2.imencode(".png", frame)
        if not ok:
            raise RuntimeError("Could not encode the captured image.")
        return encoded.tobytes()

    def save_image(self, capture: CapturedImage) -> str:
        if not capture.image:
            raise ValueError("Capture an image before saving.")
        self._directory.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
        name = f"capture_{stamp}_{uuid4().hex}"
        destination = self._directory / name
        metadata = {
            "schema_version": 1,
            "image_file": f"{name}.png",
            "captured_at": capture.captured_at,
            "width": capture.width,
            "height": capture.height,
            "coordinate_space": "calibrated_image_pixels",
            "origin": "top_left",
            "axes": {"x": "right", "y": "down"},
            "contour_count": len(capture.contours),
            "decomposition_file": f"{name}_decomposition.json",
            "decomposition_overlay_file": f"{name}_decomposition.png",
            "contours": [{"points": contour, "closed": True}
                         for contour in capture.contours],
        }
        if capture.robot_result is not None:
            metadata.update(robot_result_file=f"{name}_robot_mm.json",
                            robot_preview_file=f"{name}_robot_mm.png")
        if capture.sampled_result is not None:
            metadata.update(sampled_result_file=f"{name}_sampled_mm.json",
                            sampled_preview_file=f"{name}_sampled_mm.png")
        # Publish the directory only once all files are complete. Failed writes
        # leave no visible half-pair, and repeated saves never overwrite a pair.
        with TemporaryDirectory(dir=self._directory, prefix=".capture-") as temporary:
            staging = Path(temporary)
            (staging / f"{name}.png").write_bytes(capture.image)
            (staging / f"{name}.json").write_text(
                json.dumps(metadata, indent=2, allow_nan=False) + "\n", encoding="utf-8",
            )
            decomposition = json.loads(capture.decomposition)
            decomposition.update(source=f"{name}.json", image_file=f"{name}.png")
            (staging / f"{name}_decomposition.json").write_text(
                json.dumps(decomposition, indent=2, allow_nan=False) + "\n", encoding="utf-8",
            )
            (staging / f"{name}_decomposition.png").write_bytes(capture.decomposition_preview)
            if capture.robot_result is not None:
                robot_document = json.loads(capture.robot_result)
                robot_document.update(source=f"{name}.json", image_file=f"{name}.png")
                (staging / f"{name}_robot_mm.json").write_text(
                    json.dumps(robot_document, indent=2, allow_nan=False) + "\n", encoding="utf-8",
                )
                (staging / f"{name}_robot_mm.png").write_bytes(capture.robot_preview)
            if capture.sampled_result is not None:
                document = json.loads(capture.sampled_result)
                document['source'] = f"{name}_robot_mm.json"
                (staging / f"{name}_sampled_mm.json").write_text(json.dumps(document, indent=2, allow_nan=False), encoding="utf-8")
                (staging / f"{name}_sampled_mm.png").write_bytes(capture.sampled_preview)
            staging.rename(destination)
        return str(destination)
