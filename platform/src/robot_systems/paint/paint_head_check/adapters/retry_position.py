"""Reuse only a prepared inspection stop that still matches fresh stationary feedback."""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from src.robot_systems.paint.contracts.paint_head_check.interfaces import (
    IHeadInspectionRetryPosition,
)
from src.robot_systems.paint.contracts.paint_head_check.models import (
    HeadInspectionPose,
    HeadInspectionPositionTolerance,
    HeadInspectionTarget,
)

from .position_feedback import inspection_pose_matches, parse_inspection_pose, robot_is_stationary

type ReferenceFrame = tuple[int, int]


class IRetryPositionNavigation(Protocol):
    def get_current_observer_position(
        self, group_name: str, *, fresh: bool = False
    ) -> list[float] | None: ...
    def mark_group_observed_area_verified(self, group_name: str) -> None: ...


class IRetryPositionRobot(Protocol):
    def get_execution_status(self) -> object: ...
    def set_active_tool(self, tool: int) -> bool: ...
    def set_active_workobject(self, user: int) -> bool: ...


@dataclass(frozen=True, slots=True)
class _RetainedPosition:
    target: HeadInspectionTarget
    frame: ReferenceFrame
    pose: HeadInspectionPose


class VerifiedInspectionRetryPosition(IHeadInspectionRetryPosition):
    def __init__(
        self,
        navigation: IRetryPositionNavigation,
        robot: IRetryPositionRobot,
        frame_provider: Callable[[], ReferenceFrame],
        tolerance: HeadInspectionPositionTolerance,
        logger: logging.Logger,
    ) -> None:
        self._navigation = navigation
        self._robot = robot
        self._frame_provider = frame_provider
        self._tolerance = tolerance
        self._logger = logger
        self._retained: _RetainedPosition | None = None

    def invalidate(self) -> None:
        self._retained = None

    def remember_stop(self, target: HeadInspectionTarget) -> None:
        self.invalidate()
        feedback = self._read_feedback(target)
        if feedback is not None:
            frame, pose = feedback
            if self._matches(pose, target.position):
                self._retained = _RetainedPosition(target, frame, pose)
                self._logger.info(
                    "Paint-head inspection stop retained for a freshly verified retry"
                )

    def try_reuse(self, target: HeadInspectionTarget) -> bool:
        retained = self._retained
        if retained is None or target != retained.target:
            self.invalidate()
            return False
        feedback = self._read_feedback(target, expected_frame=retained.frame)
        if feedback is None:
            self.invalidate()
            return False
        frame, pose = feedback
        if frame != retained.frame or not (
            self._matches(pose, target.position) and self._matches(pose, retained.pose)
        ):
            self.invalidate()
            return False
        self._navigation.mark_group_observed_area_verified(target.group_id.value)
        self._logger.info(
            "Paint-head retry position verified from fresh feedback; tolerance_mm=%.3f tolerance_deg=%.3f pose=%s",
            self._tolerance.translation_mm,
            self._tolerance.rotation_degrees,
            pose,
        )
        return True

    def _read_feedback(
        self,
        target: HeadInspectionTarget,
        *,
        expected_frame: ReferenceFrame | None = None,
    ) -> tuple[ReferenceFrame, HeadInspectionPose] | None:
        try:
            frame = self._frame_provider()
            if (
                len(frame) != 2
                or any(type(value) is not int or value < 0 for value in frame)
                or (expected_frame is not None and frame != expected_frame)
                or not robot_is_stationary(self._robot.get_execution_status())
            ):
                return None
            # Coordinate-frame activation does not move the robot and makes the
            # fresh TCP read use exactly the frame of the taught inspection move.
            if not self._robot.set_active_tool(frame[0]) or not self._robot.set_active_workobject(
                frame[1]
            ):
                return None
            raw = self._navigation.get_current_observer_position(target.group_id.value, fresh=True)
            if (
                not robot_is_stationary(self._robot.get_execution_status())
                or frame != self._frame_provider()
            ):
                return None
            pose = parse_inspection_pose(raw)
            return None if pose is None else (frame, pose)
        except (OSError, ValueError, OverflowError):
            self._logger.warning(
                "Cannot verify inspection retry position; normal startup is required", exc_info=True
            )
            return None

    def _matches(self, actual: HeadInspectionPose, expected: HeadInspectionPose) -> bool:
        return inspection_pose_matches(actual, expected, self._tolerance)
