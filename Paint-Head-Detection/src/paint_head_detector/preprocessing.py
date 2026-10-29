"""Image normalization and strict inspection-boundary enforcement."""

from dataclasses import dataclass
from typing import cast

import cv2
import numpy as np

from .configuration import CalibrationConfig, PreprocessingConfig
from .errors import ConfigurationError, ErrorReason
from .models import BoolMask, DetectionReason, FloatImage, Image, ImageQuality, ImageSize


@dataclass(frozen=True, slots=True)
class PreprocessingResult:
    edges: Image
    proximity: FloatImage
    quality: ImageQuality


def edge_proximity(binary: Image | FloatImage, sigma: float) -> FloatImage:
    if not np.any(binary):
        return np.zeros(binary.shape, np.float32)
    distance = cv2.distanceTransform((binary == 0).astype(np.uint8), cv2.DIST_L2, 3)
    return cast(FloatImage, np.exp(-(distance**2) / (2 * sigma**2)))


class ImageProcessor:
    def __init__(
        self,
        calibration: CalibrationConfig,
        settings: PreprocessingConfig,
        size: ImageSize,
        edge_sigma: float,
    ) -> None:
        self._calibration = calibration
        self._settings = settings
        self._sigma = edge_sigma
        mask = np.zeros((size.height, size.width), dtype=bool)
        mask[calibration.inspection_region.slices] = True
        for region in calibration.ignored_regions:
            mask[region.slices] = False
        if np.count_nonzero(mask) < settings.minimum_valid_pixels:
            raise ConfigurationError(
                ErrorReason.CONFIGURATION_INVALID,
                f"Inspection ROI must contain at least {settings.minimum_valid_pixels} unmasked pixels",
            )
        for feature in calibration.present_features:
            if not np.all(mask[feature.region.slices]):
                raise ConfigurationError(
                    ErrorReason.CONFIGURATION_INVALID,
                    f"Present feature {feature.name!r} overlaps an ignored region",
                )
        mask.setflags(write=False)
        self._mask = mask

    @property
    def inspection_mask(self) -> BoolMask:
        return self._mask

    def process(self, image: Image) -> PreprocessingResult:
        edges = self.extract_edges(image)
        proximity = np.zeros(edges.shape, np.float32)
        region = self._calibration.inspection_region.slices
        proximity[region] = edge_proximity(edges[region], self._sigma)
        proximity[~self._mask] = 0
        return PreprocessingResult(edges, proximity, self.check_quality(image))

    def check_quality(self, image: Image) -> ImageQuality:
        p = self._settings
        region = self._calibration.inspection_region.slices
        gray = cv2.cvtColor(image[region], cv2.COLOR_BGR2GRAY)
        low, high = np.percentile(
            gray[self._mask[region]], (p.quality_low_percentile, p.quality_high_percentile)
        )
        issue = None
        if high <= p.dark_limit:
            issue = DetectionReason.TOO_DARK
        elif low >= p.bright_limit:
            issue = DetectionReason.OVEREXPOSED
        elif high - low < p.minimum_contrast:
            issue = DetectionReason.LOW_CONTRAST
        return ImageQuality(issue)

    def extract_edges(self, image: Image) -> Image:
        p = self._settings
        region = self._calibration.inspection_region.slices
        valid = self._mask[region]
        gray = cv2.cvtColor(image[region], cv2.COLOR_BGR2GRAY)
        if not np.all(valid):
            gray[~valid] = 0
            gray = cv2.inpaint(gray, (~valid).astype(np.uint8), p.inpaint_radius, cv2.INPAINT_TELEA)
        gray = cv2.GaussianBlur(gray, (p.blur_kernel, p.blur_kernel), 0)
        light = cv2.GaussianBlur(gray.astype(np.float32), (0, 0), p.illumination_sigma)
        normalized = gray.astype(np.float32) / np.maximum(light, p.illumination_floor)
        low, high = np.percentile(normalized[valid], (p.low_percentile, p.high_percentile))
        normalized = np.clip(
            (normalized - low) * 255.0 / max(high - low, p.minimum_normalization_range), 0, 255
        )
        enhanced = cv2.createCLAHE(
            clipLimit=p.clahe_clip_limit, tileGridSize=(p.clahe_tile_size, p.clahe_tile_size)
        ).apply(normalized.astype(np.uint8))
        gx = cv2.Sobel(enhanced, cv2.CV_32F, 1, 0)
        gy = cv2.Sobel(enhanced, cv2.CV_32F, 0, 1)
        strength = np.abs(gx) + np.abs(gy)
        upper = max(
            p.canny_high_floor, float(np.percentile(strength[valid], p.gradient_percentile))
        )
        extracted = cv2.Canny(enhanced, p.canny_low_ratio * upper, upper)
        extracted[~valid] = 0
        result = np.zeros(image.shape[:2], dtype=np.uint8)
        result[region] = extracted
        return result
