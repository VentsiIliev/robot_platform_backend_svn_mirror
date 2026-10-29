"""Load reference images without opening cameras or interactive selectors."""

from dataclasses import dataclass
from pathlib import Path
from typing import cast

import cv2
import numpy as np

from .configuration import DetectorConfiguration, ReferencePaths, ReferenceSource
from .errors import CalibrationError, ConfigurationError, ErrorReason, InvalidImageError
from .models import Image, ImageSize, ReferenceImages, Region


def read_image(path: Path) -> Image:
    if not path.is_file():
        raise CalibrationError(
            ErrorReason.REFERENCE_UNREADABLE, f"Image file does not exist: {path}"
        )
    try:
        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    except cv2.error as error:
        raise CalibrationError(
            ErrorReason.REFERENCE_UNREADABLE, f"Could not decode reference image {path}: {error}"
        ) from error
    if image is None:
        raise CalibrationError(ErrorReason.REFERENCE_UNREADABLE, f"Cannot read image: {path}")
    return cast(Image, image)


@dataclass(frozen=True, slots=True)
class CalibrationData:
    present_reference: Image
    missing_reference: Image
    size: ImageSize


class CalibrationLoader:
    def load_references(self, source: ReferenceSource) -> ReferenceImages:
        """Take an owned snapshot; caller arrays and their flags remain unchanged."""
        if isinstance(source, ReferencePaths):
            present = read_image(source.present)
            missing = read_image(source.missing)
        else:
            present, missing = source.present, source.missing
        for label, image in (("present", present), ("missing", missing)):
            try:
                ImageValidator.validate_format(image)
            except InvalidImageError as error:
                raise CalibrationError(
                    ErrorReason.REFERENCE_IMAGE_INVALID,
                    f"Invalid {label} reference: {error.message}",
                ) from error
        if present.shape != missing.shape:
            raise CalibrationError(
                ErrorReason.REFERENCE_SIZE_MISMATCH,
                f"Reference image shapes differ: present={present.shape}, missing={missing.shape}",
            )
        # Immutable backing buffers prevent callers from re-enabling writes.
        present = np.frombuffer(present.tobytes(), dtype=np.uint8).reshape(present.shape)
        missing = np.frombuffer(missing.tobytes(), dtype=np.uint8).reshape(missing.shape)
        return ReferenceImages(present, missing)

    def load(
        self,
        configuration: DetectorConfiguration,
        *,
        reference_images: ReferenceImages | None = None,
    ) -> CalibrationData:
        calibration = configuration.calibration
        references = (
            self.load_references(calibration.references)
            if reference_images is None
            else reference_images
        )
        present, missing = references.present, references.missing
        size = ImageSize(present.shape[1], present.shape[0])
        bounds = Region(0, 0, size.width, size.height)
        regions = (
            calibration.inspection_region,
            calibration.empty_mount_region,
            *calibration.ignored_regions,
            *(f.region for f in calibration.present_features),
            *(f.region for f in calibration.missing_features),
        )
        for region in regions:
            if not bounds.contains(region):
                raise ConfigurationError(
                    ErrorReason.CONFIGURATION_INVALID,
                    f"Region {region} exceeds reference image size {size}",
                )
        return CalibrationData(present, missing, size)


class ImageValidator:
    def __init__(self, size: ImageSize) -> None:
        self._size = size

    @staticmethod
    def validate_format(image: Image) -> None:
        if not isinstance(image, np.ndarray):
            raise InvalidImageError(
                ErrorReason.IMAGE_TYPE_INVALID,
                "Image must be a NumPy array containing a BGR uint8 frame",
            )
        if image.dtype != np.uint8:
            raise InvalidImageError(
                ErrorReason.IMAGE_DTYPE_INVALID,
                f"Image dtype must be uint8, received {image.dtype}",
            )
        if image.ndim != 3 or image.shape[2] != 3 or image.size == 0:
            raise InvalidImageError(
                ErrorReason.IMAGE_SHAPE_INVALID,
                f"Image must have shape (height, width, 3), received {image.shape}",
            )

    def validate(self, image: Image) -> None:
        self.validate_format(image)
        expected = (self._size.height, self._size.width)
        if image.shape[:2] != expected:
            raise InvalidImageError(
                ErrorReason.IMAGE_SIZE_MISMATCH,
                f"Image size {image.shape[:2]} does not match reference size {expected}",
            )
