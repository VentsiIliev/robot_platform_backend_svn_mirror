"""Settings for the headless example; detector settings remain in config/."""

from dataclasses import dataclass
from pathlib import Path

from paint_head_detector import CalibrationConfig


@dataclass(frozen=True, slots=True)
class ExampleSettings:
    config_directory: Path
    image_paths: tuple[Path, ...]
    independent_images: bool = False
    calibration: CalibrationConfig | None = None


PROJECT_DIRECTORY = Path(__file__).resolve().parents[1]

SETTINGS = ExampleSettings(
    config_directory=PROJECT_DIRECTORY / "config",
    image_paths=(
        PROJECT_DIRECTORY / "src/paint_head_dataset/references/head_present.png",
        PROJECT_DIRECTORY / "src/paint_head_dataset/references/head_missing.png",
    ),
    independent_images=True,
)
