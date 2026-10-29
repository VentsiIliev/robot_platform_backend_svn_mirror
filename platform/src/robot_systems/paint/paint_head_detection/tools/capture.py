#!/usr/bin/env python3
"""Run paint-head capture and benchmarks. Supports module and direct-file execution."""

import sys
from pathlib import Path

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[5]))

from src.robot_systems.paint.paint_head_detection.development.capture_cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
