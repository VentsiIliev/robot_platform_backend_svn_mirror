"""Command-line overrides are a development concern, not detector configuration."""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass, replace
from pathlib import Path
from typing import TypeVar

from ..configuration import DEFAULT_CONFIG_DIRECTORY, ConfigurationRepository, DetectorConfiguration
from ..errors import ConfigurationError, ErrorReason
from .settings import DevelopmentSettings, DevelopmentSettingsRepository

T = TypeVar("T")


def _choose[T](value: T | None, configured: T) -> T:
    return configured if value is None else value


def _device(value: str) -> int | str:
    return int(value) if value.isdecimal() else value


@dataclass
class DevelopmentArguments(argparse.Namespace):
    config_dir: Path = DEFAULT_CONFIG_DIRECTORY
    select_features: bool = False
    select_missing_features: bool = False
    camera: int | str | None = None
    camera_format: str | None = None
    camera_fps: float | None = None
    opencv_threads: int | None = None
    headless: bool | None = None
    show_edges: bool | None = None
    show_expected: bool | None = None
    duration: float | None = None
    capture_dir: Path | None = None
    capture_interval: float | None = None
    search_margin: int | None = None
    relative_tolerance: float | None = None
    plate_threshold: float | None = None
    min_missing_features: int | None = None
    stable_frames: int | None = None
    max_rotation: int | None = None
    rotation_step: int | None = None
    consensus_tolerance: float | None = None
    min_present_features: int | None = None
    alignment_pixels: float | None = None
    alignment_degrees: float | None = None
    alignment_hysteresis_pixels: float | None = None
    alignment_hysteresis_degrees: float | None = None
    unknown_grace_frames: int | None = None
    unknown_grace_seconds: float | None = None
    exposure_sweep: bool = False
    show: bool = False
    benchmark: bool = False


@dataclass(frozen=True, slots=True)
class DevelopmentOptions:
    configuration: DetectorConfiguration
    development: DevelopmentSettings
    config_directory: Path
    headless: bool
    duration: float
    capture_directory: Path | None
    select_present: bool
    select_missing: bool
    exposure_sweep: bool
    benchmark: bool


def argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Paint-head detector development tools; defaults come from config/"
    )
    parser.add_argument("--config-dir", type=Path, default=DEFAULT_CONFIG_DIRECTORY)
    parser.add_argument("--select-features", action="store_true")
    parser.add_argument("--select-missing-features", action="store_true")
    parser.add_argument("--camera", type=_device)
    parser.add_argument("--camera-format")
    parser.add_argument("--camera-fps", type=float)
    parser.add_argument("--opencv-threads", type=int)
    parser.add_argument("--headless", action=argparse.BooleanOptionalAction)
    parser.add_argument("--show-edges", action=argparse.BooleanOptionalAction)
    parser.add_argument("--show-expected", action=argparse.BooleanOptionalAction)
    parser.add_argument("--duration", type=float)
    parser.add_argument("--capture-dir", type=Path)
    parser.add_argument("--capture-interval", type=float)
    parser.add_argument("--search-margin", type=int)
    parser.add_argument("--relative-tolerance", type=float)
    parser.add_argument("--plate-threshold", type=float)
    parser.add_argument("--min-missing-features", type=int)
    parser.add_argument("--stable-frames", type=int)
    parser.add_argument("--max-rotation", type=int)
    parser.add_argument("--rotation-step", type=int)
    parser.add_argument("--consensus-tolerance", type=float)
    parser.add_argument("--min-present-features", type=int)
    parser.add_argument("--alignment-pixels", type=float)
    parser.add_argument("--alignment-degrees", type=float)
    parser.add_argument("--alignment-hysteresis-pixels", type=float)
    parser.add_argument("--alignment-hysteresis-degrees", type=float)
    parser.add_argument("--unknown-grace-frames", type=int)
    parser.add_argument("--unknown-grace-seconds", type=float)
    parser.add_argument("--exposure-sweep", action="store_true")
    parser.add_argument(
        "--show", action="store_true", help="Show development windows while capturing"
    )
    parser.add_argument("--benchmark", action="store_true")
    return parser


def parse_options(
    argv: list[str] | None = None, *, capture_mode: bool = False
) -> DevelopmentOptions:
    args = argument_parser().parse_args(argv, namespace=DevelopmentArguments())
    config = ConfigurationRepository(args.config_dir).load()
    development = DevelopmentSettingsRepository(args.config_dir).load()
    m, a, c, r, v = (
        config.matching,
        config.alignment,
        development.camera,
        development.runtime,
        development.view,
    )
    matching = replace(
        m,
        search_margin=_choose(args.search_margin, m.search_margin),
        relative_tolerance=_choose(args.relative_tolerance, m.relative_tolerance),
        plate_threshold=_choose(args.plate_threshold, m.plate_threshold),
        min_missing_features=_choose(args.min_missing_features, m.min_missing_features),
        max_rotation=_choose(args.max_rotation, m.max_rotation),
        rotation_step=_choose(args.rotation_step, m.rotation_step),
        consensus_tolerance=_choose(args.consensus_tolerance, m.consensus_tolerance),
        min_present_features=_choose(args.min_present_features, m.min_present_features),
    )
    alignment = replace(
        a,
        stable_frames=_choose(args.stable_frames, a.stable_frames),
        max_translation_pixels=_choose(args.alignment_pixels, a.max_translation_pixels),
        max_rotation_degrees=_choose(args.alignment_degrees, a.max_rotation_degrees),
        hysteresis_pixels=_choose(args.alignment_hysteresis_pixels, a.hysteresis_pixels),
        hysteresis_degrees=_choose(args.alignment_hysteresis_degrees, a.hysteresis_degrees),
        unknown_grace_frames=_choose(args.unknown_grace_frames, a.unknown_grace_frames),
        unknown_grace_seconds=_choose(args.unknown_grace_seconds, a.unknown_grace_seconds),
    )
    camera = replace(
        c,
        device=_choose(args.camera, c.device),
        fourcc=_choose(args.camera_format, c.fourcc),
        fps=_choose(args.camera_fps, c.fps),
    )
    runtime = replace(
        r,
        opencv_threads=_choose(args.opencv_threads, r.opencv_threads),
        capture_interval=_choose(args.capture_interval, r.capture_interval),
    )
    view = replace(
        v,
        show_edges=_choose(args.show_edges, v.show_edges),
        show_expected=_choose(args.show_expected, v.show_expected),
    )
    configuration = replace(config, matching=matching, alignment=alignment)
    configuration.validate()
    headless = _choose(args.headless, not args.show if capture_mode else runtime.headless)
    duration = _choose(
        args.duration, runtime.capture_duration if capture_mode else runtime.duration
    )
    if (
        any(not math.isfinite(value) for value in (duration, runtime.capture_interval, camera.fps))
        or duration < 0
        or runtime.capture_interval <= 0
        or runtime.opencv_threads < 1
        or camera.fps <= 0
        or len(camera.fourcc) != 4
    ):
        raise ConfigurationError(
            ErrorReason.CONFIGURATION_INVALID,
            "Invalid runtime duration, interval, threads, camera format, or frame rate",
        )
    if headless and duration <= 0 and not args.benchmark:
        raise ConfigurationError(
            ErrorReason.CONFIGURATION_INVALID, "Headless operation requires a positive duration"
        )
    if capture_mode and duration <= 0 and not args.benchmark:
        raise ConfigurationError(
            ErrorReason.CONFIGURATION_INVALID, "Capture duration must be positive"
        )
    return DevelopmentOptions(
        configuration,
        DevelopmentSettings(camera, runtime, view),
        args.config_dir,
        headless,
        duration,
        args.capture_dir,
        args.select_features,
        args.select_missing_features,
        args.exposure_sweep,
        args.benchmark,
    )
