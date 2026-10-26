from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class CapturedImage:
    """One frozen image and its contours in calibrated-image pixel coordinates."""

    image: bytes
    preview: bytes
    contours: tuple[tuple[tuple[float, float], ...], ...]
    width: int
    height: int
    captured_at: str
    decomposition: bytes
    decomposition_preview: bytes
    line_count: int = 0
    arc_count: int = 0
    exceeds_tolerance: int = 0
    failed_contours: int = 0
    robot_result: bytes | None = None
    robot_preview: bytes | None = None
    sampled_result: bytes | None = None
    sampled_preview: bytes | None = None


class IImageCaptureService(ABC):
    @abstractmethod
    def capture(self) -> CapturedImage:
        """Capture, detect contours, and decompose them into lines and arcs."""

    @abstractmethod
    def save_image(self, capture: CapturedImage) -> str:
        """Save a complete PNG/JSON pair and return its directory."""

    @abstractmethod
    def output_directory(self) -> str:
        """Return the configured image storage directory."""
