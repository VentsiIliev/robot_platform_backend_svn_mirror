from dataclasses import replace
import cv2
import numpy as np
from src.engine.geometry.contour_to_dxf import write_contour_dxf
from src.engine.geometry.rectangle_scale_calibration import calibrate_rectangle_scale
from .i_contour_dxf_service import IContourDXFService, FrameData, CaptureData, SessionInfo

class ContourDXFService(IContourDXFService):
    """Camera adapter with injected processing and script-local calibration storage."""
    def __init__(self, vision_factory, capture_geometry, save_calibration, *, source,
                 base_scale, correction, output_dir, calibration_path):
        self._vision_factory = vision_factory
        self._capture_geometry = capture_geometry
        self._save_calibration = save_calibration
        self._base_scale = base_scale
        self._info = SessionInfo(source, base_scale * correction, correction, str(output_dir), str(calibration_path))
        self._vision = None
        self._capture = None
        self._contour = None

    def start(self):
        if self._vision is not None:
            return
        vision = self._vision_factory()
        try:
            vision.start()
        except Exception:
            vision.stop()
            raise
        self._vision = vision

    def stop(self):
        vision, self._vision = self._vision, None
        if vision is not None:
            vision.stop()

    def get_info(self):
        return self._info

    @staticmethod
    def _frame(image):
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB if image.ndim == 2 else cv2.COLOR_BGR2RGB)
        image = np.ascontiguousarray(image)
        return FrameData(image.shape[1], image.shape[0], image.tobytes())

    def get_live_frame(self):
        vision = self._vision
        if vision is None:
            return None
        frame = vision.get_latest_frame()
        return None if frame is None else self._frame(frame)

    def _measure(self, scale, smooth, exportable):
        if self._vision is None:
            raise ValueError('Connect the camera first')
        image, contour, _box, size = self._capture_geometry(self._vision, scale, smooth)
        self._contour = np.array(contour, copy=True)
        self._capture = CaptureData(self._frame(image), float(size[0]) * scale, float(size[1]) * scale, len(contour), exportable)
        return self._capture

    def capture(self, smooth):
        return self._measure(self._info.mm_per_pixel, smooth, True)

    def get_capture(self):
        return self._capture

    def calibrate(self, width_mm, height_mm, tolerance_percent):
        if not np.isfinite(tolerance_percent) or tolerance_percent <= 0:
            raise ValueError('Tolerance must be finite and positive')
        measured = self._measure(self._base_scale, False, False)
        result = calibrate_rectangle_scale((measured.width_mm, measured.height_mm), (width_mm, height_mm))
        if max(abs(value) for value in result.residual_percent) > tolerance_percent:
            raise ValueError(f'Reference sides disagree: {result.residual_percent}%')
        self._save_calibration(result)
        self._info = replace(self._info, correction=result.correction, mm_per_pixel=self._base_scale * result.correction, residual_mm=result.residual_mm)
        self._capture = replace(measured, width_mm=measured.width_mm * result.correction, height_mm=measured.height_mm * result.correction)

    def export(self, destination):
        if self._capture is None or not self._capture.exportable:
            raise ValueError('Capture a part before exporting')
        saved = write_contour_dxf(destination, self._contour, self._info.mm_per_pixel)
        self._info = replace(self._info, last_export=str(saved))
