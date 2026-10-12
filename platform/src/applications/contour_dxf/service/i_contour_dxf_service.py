"""Qt-free contract for the contour studio."""
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass(frozen=True)
class FrameData:
    width: int
    height: int
    rgb: bytes

@dataclass(frozen=True)
class CaptureData:
    preview: FrameData
    width_mm: float
    height_mm: float
    point_count: int
    exportable: bool = True

@dataclass(frozen=True)
class SessionInfo:
    source: str
    mm_per_pixel: float
    correction: float
    output_dir: str
    calibration_path: str
    residual_mm: tuple[float, float] | None = None
    last_export: str = ''

class IContourDXFService(ABC):
    @abstractmethod
    def start(self) -> None: ...
    @abstractmethod
    def stop(self) -> None: ...
    @abstractmethod
    def get_info(self) -> SessionInfo: ...
    @abstractmethod
    def get_live_frame(self) -> FrameData | None: ...
    @abstractmethod
    def capture(self, smooth: bool) -> CaptureData: ...
    @abstractmethod
    def get_capture(self) -> CaptureData | None: ...
    @abstractmethod
    def calibrate(self, width_mm: float, height_mm: float, tolerance_percent: float) -> None: ...
    @abstractmethod
    def export(self, destination: str) -> None: ...
