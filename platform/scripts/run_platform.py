"""Launch the PyQt application without OpenCV's bundled Qt environment."""
import os
from pathlib import Path
import runpy


def prepare_qt_environment() -> None:
    """Import OpenCV once, then restore the caller's Qt plugin/font settings."""
    keys = ("QT_QPA_PLATFORM_PLUGIN_PATH", "QT_QPA_FONTDIR")
    original = {key: os.environ.get(key) for key in keys}
    import cv2  # noqa: F401 -- initializes OpenCV before restoring Qt settings

    for key, value in original.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


if __name__ == "__main__":
    prepare_qt_environment()
    runpy.run_path(str(Path(__file__).resolve().parents[1] / "src/bootstrap/run_main.py"),
                   run_name="__main__")
