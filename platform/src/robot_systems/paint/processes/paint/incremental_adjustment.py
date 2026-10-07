"""Operator-paced paint-contact execution; no Qt or application dependencies."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import dist, isfinite
from threading import Condition
from typing import Callable, NamedTuple, Sequence, TypeAlias


@dataclass(frozen=True)
class AdjustmentStep:
    length_mm: float
    paint_axis_offset_mm: float
    perpendicular_axis_offset_mm: float

    def validate(self) -> None:
        values = (self.length_mm, self.paint_axis_offset_mm, self.perpendicular_axis_offset_mm)
        if not all(isfinite(float(value)) for value in values):
            raise ValueError("Adjustment distances must be finite")
        if not 0.1 <= self.length_mm <= 100.0:
            raise ValueError("Paint length must be between 0.1 and 100 mm")
        if abs(self.paint_axis_offset_mm) < 1.0:
            raise ValueError("Paint-axis inspection offset must be at least 1 mm")
        if any(abs(value) > 200.0 for value in values[1:]):
            raise ValueError("Inspection offsets must be within ±200 mm")


DEFAULT_ADJUSTMENT_STEP = AdjustmentStep(10.0, 0.0, 0.0)


class PaintPathCursor:
    """Consume a six-axis command path by Cartesian XYZ arc length."""

    def __init__(self, path: Sequence[Sequence[float]]) -> None:
        self._path = [tuple(float(value) for value in pose) for pose in path]
        if len(self._path) < 2 or any(len(pose) != 6 for pose in self._path):
            raise ValueError("Paint path requires at least two six-axis poses")
        self._index = 0
        self._current = self._path[0]
        self.travelled_mm = 0.0
        self.total_mm = sum(dist(a[:3], b[:3]) for a, b in zip(self._path, self._path[1:]))
        if self.total_mm <= 1e-6:
            raise ValueError("Paint path has no Cartesian travel")

    @property
    def complete(self) -> bool:
        return self._index >= len(self._path) - 1

    @property
    def current_pose(self) -> tuple[float, ...]:
        return self._current

    def take(self, length_mm: float) -> list[tuple[float, ...]]:
        if not isfinite(length_mm) or length_mm <= 0:
            raise ValueError("Paint length must be positive and finite")
        if self.complete:
            return []
        remaining = length_mm
        chunk = [self._current]
        while remaining > 1e-8 and not self.complete:
            end = self._path[self._index + 1]
            edge = dist(self._current[:3], end[:3])
            if edge <= 1e-8:
                self._current = end
                self._index += 1
                if chunk[-1] != end:
                    chunk.append(end)
                continue
            if edge <= remaining + 1e-8:
                self._current = end
                self._index += 1
                self.travelled_mm += edge
                remaining -= edge
            else:
                ratio = remaining / edge
                self._current = tuple(
                    start + ratio * (finish - start)
                    for start, finish in zip(self._current, end)
                )
                self.travelled_mm += remaining
                remaining = 0.0
            if chunk[-1] != self._current:
                chunk.append(self._current)
        return chunk


class AdjustmentPhase(StrEnum):
    STARTING = "starting"
    WAITING_FOR_WORKPIECE = "waiting_for_workpiece"
    INSPECT = "inspect"
    MOVING = "moving"
    FINISHING = "finishing"
    ERROR = "error"


class AdjustmentSnapshot(NamedTuple):
    phase: AdjustmentPhase
    travelled_mm: float
    total_mm: float


@dataclass(frozen=True)
class NextPaintSection:
    step: AdjustmentStep

    def __post_init__(self) -> None:
        if not isinstance(self.step, AdjustmentStep):
            raise TypeError("Next paint section requires an AdjustmentStep")
        self.step.validate()


@dataclass(frozen=True)
class FinishAdjustment:
    pass


@dataclass(frozen=True)
class CancelAdjustment:
    pass


AdjustmentCommand: TypeAlias = NextPaintSection | FinishAdjustment | CancelAdjustment


class PaintAdjustmentSession:
    """Single operator command slot with explicit inspect and finish states."""

    def __init__(self) -> None:
        self._condition = Condition()
        self._command: NextPaintSection | FinishAdjustment | None = None
        self._phase = AdjustmentPhase.STARTING
        self._complete = False
        self._travelled_mm = 0.0
        self._total_mm = 0.0

    def snapshot(self) -> AdjustmentSnapshot:
        with self._condition:
            return AdjustmentSnapshot(self._phase, self._travelled_mm, self._total_mm)

    def workpiece_not_found(self) -> None:
        with self._condition:
            self._phase = AdjustmentPhase.WAITING_FOR_WORKPIECE

    def workpiece_found(self) -> None:
        with self._condition:
            if self._phase is AdjustmentPhase.WAITING_FOR_WORKPIECE:
                self._phase = AdjustmentPhase.STARTING

    def inspection_ready(self, travelled_mm: float, total_mm: float, *, complete: bool) -> None:
        with self._condition:
            self._phase = AdjustmentPhase.INSPECT
            self._travelled_mm = travelled_mm
            self._total_mm = total_mm
            self._complete = complete
            self._condition.notify_all()

    def request_next(self, step: AdjustmentStep) -> bool:
        step.validate()
        with self._condition:
            if self._phase is not AdjustmentPhase.INSPECT or self._complete or self._command is not None:
                return False
            self._command = NextPaintSection(step)
            self._phase = AdjustmentPhase.MOVING
            self._condition.notify_all()
            return True

    def request_finish(self) -> bool:
        with self._condition:
            # Before the first section the robot is still at the pickup staging pose,
            # not at a known inspection pose from which dropoff can be planned.
            if self._phase is not AdjustmentPhase.INSPECT or self._travelled_mm <= 1e-6 or self._command is not None:
                return False
            self._command = FinishAdjustment()
            self._phase = AdjustmentPhase.FINISHING
            self._condition.notify_all()
            return True

    def wait_for_command(self, should_stop: Callable[[], bool]) -> tuple[str, AdjustmentStep | None] | None:
        """Legacy command adapter; execution consumes wait_for_command_result."""
        command = self.wait_for_command_result(should_stop)
        if isinstance(command, CancelAdjustment):
            return None
        if isinstance(command, FinishAdjustment):
            return "finish", None
        return "next", command.step

    def wait_for_command_result(self, should_stop: Callable[[], bool]) -> AdjustmentCommand:
        with self._condition:
            while self._command is None:
                if should_stop():
                    return CancelAdjustment()
                self._condition.wait(timeout=0.1)
            if should_stop():
                self._command = None
                return CancelAdjustment()
            command = self._command
            self._command = None
            assert command is not None
            return command

    def fail(self) -> None:
        with self._condition:
            self._phase = AdjustmentPhase.ERROR
