"""Typed camera, UI, and capture settings loaded separately from detector settings."""

import math
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import cast

from ..configuration import DEFAULT_CONFIG_DIRECTORY, JsonReader

type Color = tuple[int, int, int]


class CameraBackend(Enum):
    AUTO = "AUTO"
    ANY = "ANY"
    V4L2 = "V4L2"
    DSHOW = "DSHOW"
    FFMPEG = "FFMPEG"


@dataclass(frozen=True, slots=True)
class CameraSettings:
    device: int | str
    width: int
    height: int
    fourcc: str
    fps: float
    open_timeout: float
    retries: int
    backend: CameraBackend
    read_timeout: float
    retry_delay: float
    configuration_settle_delay: float
    control_settle_delay: float
    stream_release_delay: float
    automatic_exposure_values: tuple[float, ...]
    manual_exposure_values: tuple[float, ...]
    automatic_exposure_modes: tuple[float, ...]
    manual_exposure_modes: tuple[float, ...]
    exposure_absolute_tolerance: float
    exposure_relative_tolerance: float


@dataclass(frozen=True, slots=True)
class CameraProperties:
    width: int
    height: int
    fps: float
    fourcc: int
    backend_name: str


@dataclass(frozen=True, slots=True)
class ViewSettings:
    show_edges: bool
    show_expected: bool
    main_width: int
    main_height: int
    edges_width: int
    edges_height: int
    main_title: str
    edges_title: str
    fps_window: int
    dash_period: int
    dash_length: int
    present_color: Color
    misaligned_color: Color
    missing_color: Color
    unknown_color: Color
    expected_color: Color
    ignored_color: Color


@dataclass(frozen=True, slots=True)
class RuntimeSettings:
    opencv_threads: int
    headless: bool
    duration: float
    capture_duration: float
    capture_interval: float
    output_directory: Path
    benchmark_frames: int
    warmup_frames: int
    exposure_calibration_attempts: int
    exposure_brightness_tolerance: float
    exposure_brightness_floor: float
    exposure_ratio_min: float
    exposure_ratio_max: float
    exposure_factors: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class DevelopmentSettings:
    camera: CameraSettings
    runtime: RuntimeSettings
    view: ViewSettings


def _numbers(reader: JsonReader, key: str) -> tuple[float, ...]:
    values = reader.sequence(key)
    if not values or any(
        isinstance(v, bool) or not isinstance(v, (float, int)) or not math.isfinite(v)
        for v in values
    ):
        reader.fail(key, "expected a non-empty array of numbers")
    return tuple(float(cast(float | int, value)) for value in values)


def _color(reader: JsonReader, key: str) -> Color:
    values = reader.sequence(key)
    if len(values) != 3 or any(
        isinstance(v, bool) or not isinstance(v, int) or not 0 <= v <= 255 for v in values
    ):
        reader.fail(key, "expected three integer BGR channels between 0 and 255")
    return cast(int, values[0]), cast(int, values[1]), cast(int, values[2])


class DevelopmentSettingsRepository:
    def __init__(self, directory: Path = DEFAULT_CONFIG_DIRECTORY) -> None:
        self.directory = directory.resolve()

    def load(self) -> DevelopmentSettings:
        root = JsonReader.read(self.directory / "development.json")
        c, r, v = root.child("camera"), root.child("runtime"), root.child("view")
        device = c.value("device")
        if isinstance(device, bool) or not isinstance(device, (str, int)):
            c.fail("device", "expected a camera index or device path")
        try:
            backend = CameraBackend(c.text("backend"))
        except ValueError as error:
            c.fail("backend", str(error))
            raise AssertionError("unreachable") from error
        camera = CameraSettings(
            cast(int | str, device),
            c.integer("width"),
            c.integer("height"),
            c.text("fourcc"),
            c.number("fps"),
            c.number("open_timeout"),
            c.integer("retries"),
            backend,
            c.number("read_timeout"),
            c.number("retry_delay"),
            c.number("configuration_settle_delay"),
            c.number("control_settle_delay"),
            c.number("stream_release_delay"),
            _numbers(c, "automatic_exposure_values"),
            _numbers(c, "manual_exposure_values"),
            _numbers(c, "automatic_exposure_modes"),
            _numbers(c, "manual_exposure_modes"),
            c.number("exposure_absolute_tolerance"),
            c.number("exposure_relative_tolerance"),
        )
        runtime = RuntimeSettings(
            r.integer("opencv_threads"),
            r.boolean("headless"),
            r.number("duration"),
            r.number("capture_duration"),
            r.number("capture_interval"),
            (self.directory / r.text("output_directory")).resolve(),
            r.integer("benchmark_frames"),
            r.integer("warmup_frames"),
            r.integer("exposure_calibration_attempts"),
            r.number("exposure_brightness_tolerance"),
            r.number("exposure_brightness_floor"),
            r.number("exposure_ratio_min"),
            r.number("exposure_ratio_max"),
            _numbers(r, "exposure_factors"),
        )
        view = ViewSettings(
            v.boolean("show_edges"),
            v.boolean("show_expected"),
            v.integer("main_width"),
            v.integer("main_height"),
            v.integer("edges_width"),
            v.integer("edges_height"),
            v.text("main_title"),
            v.text("edges_title"),
            v.integer("fps_window"),
            v.integer("dash_period"),
            v.integer("dash_length"),
            _color(v, "present_color"),
            _color(v, "misaligned_color"),
            _color(v, "missing_color"),
            _color(v, "unknown_color"),
            _color(v, "expected_color"),
            _color(v, "ignored_color"),
        )
        if (
            camera.width < 2
            or camera.height < 2
            or camera.fps <= 0
            or len(camera.fourcc) != 4
            or camera.open_timeout <= 0
            or camera.read_timeout <= 0
            or camera.retries < 1
        ):
            c.fail("camera", "invalid size, format, frame rate, retry count, or timeout")
        if (
            runtime.opencv_threads < 1
            or runtime.duration < 0
            or runtime.capture_duration <= 0
            or runtime.capture_interval <= 0
            or runtime.benchmark_frames < 1
            or runtime.warmup_frames < 1
            or runtime.exposure_calibration_attempts < 1
        ):
            r.fail(
                "runtime",
                "thread/frame counts and intervals must be positive; duration must be non-negative",
            )
        if (
            min(
                view.main_width,
                view.main_height,
                view.edges_width,
                view.edges_height,
                view.dash_period,
                view.dash_length,
            )
            < 1
            or view.fps_window < 2
        ):
            v.fail(
                "view", "window dimensions and dash sizes must be positive; FPS window must be >= 2"
            )
        return DevelopmentSettings(camera, runtime, view)
