"""Read-only position validation for operator guidance; never select a tool or move."""

from collections.abc import Callable
from typing import Protocol

from src.robot_systems.paint.contracts.paint_head_check.errors import (
    HeadInspectionFailure,
    HeadInspectionFailureCode,
    PaintHeadCheckError,
)
from src.robot_systems.paint.contracts.paint_head_check.interfaces import (
    IHeadInspectionTargetProvider,
)
from src.robot_systems.paint.contracts.paint_head_check.models import (
    HeadInspectionPositionTolerance,
    HeadInspectionTarget,
)

from .position_feedback import inspection_pose_matches, parse_inspection_pose, robot_is_stationary


class IGuidancePositionNavigation(Protocol):
    def get_current_observer_position(
        self, group_name: str, *, fresh: bool = False
    ) -> list[float] | None: ...


class IGuidanceRobotFeedback(Protocol):
    def get_execution_status(self) -> object: ...


class PaintHeadGuidancePositionGuard:
    def __init__(
        self,
        navigation: IGuidancePositionNavigation,
        robot: IGuidanceRobotFeedback,
        target_provider: IHeadInspectionTargetProvider,
        permitted: Callable[[], bool],
        tolerance: HeadInspectionPositionTolerance,
    ) -> None:
        self._navigation = navigation
        self._robot = robot
        self._target_provider = target_provider
        self._permitted = permitted
        self._tolerance = tolerance

    def check(self, target: HeadInspectionTarget) -> HeadInspectionFailure | None:
        try:
            if not self._permitted():
                return HeadInspectionFailure(
                    HeadInspectionFailureCode.SERVICE_UNAVAILABLE,
                    "Live guidance is no longer enabled for this stopped process",
                )
            if self._target_provider.resolve() != target:
                return _position_changed()
            if not robot_is_stationary(self._robot.get_execution_status()):
                return _position_changed()
            raw = self._navigation.get_current_observer_position(target.group_id.value, fresh=True)
            pose = parse_inspection_pose(raw)
            if (
                pose is None
                or not inspection_pose_matches(pose, target.position, self._tolerance)
                or not robot_is_stationary(self._robot.get_execution_status())
            ):
                return _position_changed()
        except PaintHeadCheckError as error:
            return error.failure
        except (OSError, ValueError, OverflowError):
            return _position_changed()
        return None


def _position_changed() -> HeadInspectionFailure:
    return HeadInspectionFailure(
        HeadInspectionFailureCode.INSPECTION_POSITION_CHANGED,
        "Live guidance stopped because the robot moved or its inspection pose could not be verified",
    )
