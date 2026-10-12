"""Deterministic camera-free demo; exports use the same pure geometry utilities."""
from dataclasses import replace
from pathlib import Path

import cv2
import numpy as np

from src.engine.geometry.contour_to_dxf import write_contour_dxf
from src.engine.geometry.rectangle_scale_calibration import calibrate_rectangle_scale
from .i_contour_dxf_service import IContourDXFService, FrameData, CaptureData, SessionInfo


class StubContourDXFService(IContourDXFService):
    def __init__(self, output_dir):
        self._info = SessionInfo('DEMO · paint', 1 / 3, 1, str(output_dir), 'Demo session')
        self._started = False
        self._captured = None
        self._contour = np.array([[170, 95], [490, 95], [510, 115], [510, 375],
                                 [490, 395], [170, 395], [150, 375], [150, 115]])
        image = np.full((480, 660, 3), 35, dtype=np.uint8)
        for coordinate in range(0, 660, 30):
            cv2.line(image, (coordinate, 0), (coordinate, 480), (44, 44, 44), 1)
        for coordinate in range(0, 480, 30):
            cv2.line(image, (0, coordinate), (660, coordinate), (44, 44, 44), 1)
        cv2.fillPoly(image, [self._contour], (222, 222, 222))
        self._live = FrameData(660, 480, image.tobytes())
        cv2.polylines(image, [self._contour], True, (72, 201, 123), 2)
        cv2.rectangle(image, (150, 95), (510, 395), (246, 188, 77), 1)
        self._preview = FrameData(660, 480, image.tobytes())

    def start(self):
        self._started = True

    def stop(self):
        self._started = False

    def get_info(self):
        return self._info

    def get_live_frame(self):
        return self._live if self._started else None

    def capture(self, smooth):
        if not self._started:
            raise ValueError('Connect the camera first')
        self._captured = CaptureData(self._preview, 360 * self._info.mm_per_pixel,
                                     300 * self._info.mm_per_pixel, len(self._contour))
        return self._captured

    def get_capture(self):
        return self._captured

    def calibrate(self, width_mm, height_mm, tolerance_percent):
        if not self._started:
            raise ValueError('Connect the camera first')
        if not np.isfinite(tolerance_percent) or tolerance_percent <= 0:
            raise ValueError('Tolerance must be finite and positive')
        self._captured = CaptureData(self._preview, 120, 100, len(self._contour), False)
        result = calibrate_rectangle_scale((120, 100), (width_mm, height_mm))
        if max(abs(value) for value in result.residual_percent) > tolerance_percent:
            raise ValueError('Reference sides disagree')
        self._info = replace(self._info, correction=result.correction,
                             mm_per_pixel=result.correction / 3, residual_mm=result.residual_mm)
        self._captured = replace(self._captured, width_mm=120 * result.correction, height_mm=100 * result.correction)

    def export(self, destination):
        if self._captured is None or not self._captured.exportable:
            raise ValueError('Capture a part before exporting')
        write_contour_dxf(destination, self._contour, self._info.mm_per_pixel)
        self._info = replace(self._info, last_export=str(Path(destination)))
