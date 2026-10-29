"""Settings for the headless example; detector settings remain in config/."""

from dataclasses import dataclass
from pathlib import Path

from src.robot_systems.paint.paint_head_detection import CalibrationConfig


@dataclass(frozen=True, slots=True)
class ExampleSettings:
    config_directory: Path
    image_paths: tuple[Path, ...]
    independent_images: bool = False
    calibration: CalibrationConfig | None = None


MODULE_DIRECTORY = Path(__file__).resolve().parents[1]

SETTINGS = ExampleSettings(
    config_directory=MODULE_DIRECTORY / "config",
    image_paths=(
        MODULE_DIRECTORY / "references/head_present.png",
        MODULE_DIRECTORY / "references/head_missing.png",
    ),
    independent_images=True,
)
