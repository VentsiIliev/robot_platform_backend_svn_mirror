import logging
import os
from pathlib import Path

from src.engine.diagnostics.runtime import DiagnosticsRuntime, default_directory

_runtime: DiagnosticsRuntime | None = None


def get_diagnostics_runtime() -> DiagnosticsRuntime | None:
    return _runtime


def diagnostics_directory() -> Path:
    return default_directory()

# OpenCV writes video backend warnings directly through its native logger,
# outside Python's logging hierarchy. Set this before cv2 is imported.
os.environ.setdefault("OPENCV_LOG_LEVEL", "ERROR")


class _ColorFormatter(logging.Formatter):
    _RESET  = "\033[0m"
    _COLORS = {
        logging.DEBUG:    "\033[36m",   # cyan
        logging.INFO:     "\033[32m",   # green
        logging.WARNING:  "\033[33m",   # yellow
        logging.ERROR:    "\033[31m",   # red
        logging.CRITICAL: "\033[1;31m", # bold red
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self._COLORS.get(record.levelno, self._RESET)
        return f"{color}{super().format(record)}{self._RESET}"


def setup_logging() -> None:
    global _runtime
    handler = logging.StreamHandler()
    handler.setFormatter(_ColorFormatter(
        fmt="%(asctime)s [%(levelname)-8s] %(name)s.%(funcName)s — %(message)s",
        datefmt="%H:%M:%S",
    ))
    # INFO is the shipping default. Enable DEBUG explicitly during diagnosis.
    level = getattr(logging, os.environ.get("ROBOT_PLATFORM_LOG_LEVEL", "INFO").upper(), logging.INFO)
    if not isinstance(level, int):
        level = logging.INFO
    handler.setLevel(level)
    logging.basicConfig(level=level, handlers=[handler])
    if _runtime is None:
        _runtime = DiagnosticsRuntime(diagnostics_directory(),
            machine_id=os.environ.get("ROBOT_PLATFORM_MACHINE_ID", ""))
        _runtime.start()

    # suppress noisy third-party loggers
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("websockets").setLevel(logging.WARNING)
    logging.getLogger("websockets.client").setLevel(logging.WARNING)
    logging.getLogger("websockets.client.parse").setLevel(logging.WARNING)
