# -*- mode: python ; coding: utf-8 -*-
"""Compatibility spec for the default paint target; prefer packaging/platform/build.sh."""
import os
import sys
from pathlib import Path
ROOT = Path.cwd().resolve()
sys.path.insert(0, str(ROOT / "packaging/platform"))
from targets import prepare_target
os.environ["ROBOT_PLATFORM_BUILD_TARGET"] = "paint"
prepare_target("paint", ROOT / "build/platform-config/paint")
exec(compile((ROOT / "packaging/platform/platform.spec").read_text(), str(ROOT / "packaging/platform/platform.spec"), "exec"))
