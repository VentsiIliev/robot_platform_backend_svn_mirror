"""Translate validated inspection targets through the public paint-navigation API."""

from collections.abc import Callable
from typing import Protocol

from src.robot_systems.paint.contracts.paint_head_check.errors import (
    HeadInspectionFailure,
    HeadInspectionFailureCode,
)
from src.robot_systems.paint.contracts.paint_head_check.interfaces import (
    IHeadInspectionControl,
    IHeadInspectionMotion,
)
from src.robot_systems.paint.contracts.paint_head_check.models import (
    HeadInspectionMotionType,
    HeadInspectionTarget,
)
from src.robot_systems.paint.contracts.paint_head_check.results import (
    HeadInspectionMoveCancelled,
    HeadInspectionMoveFailed,
    HeadInspectionMovePaused,
    HeadInspectionMoveResult,
    HeadInspectionPositionReached,
)


class IPaintInspectionNavigation(Protocol):
    def move_to_position(
        self,
        position: list[float],
        group_name: str,
        wait_cancelled: Callable[[], bool] | None = None,
        velocity: float | None = None,
        acceleration: float | None = None,
        motion_type: str | None = None,
        blendR: float | None = None,
    ) -> bool: ...


_MOTION_TYPES = {
    HeadInspectionMotionType.POINT_TO_POINT: "ptp",
    HeadInspectionMotionType.LINEAR: "linear",
    HeadInspectionMotionType.FAST_LINEAR: "fast_lin",
}


class PaintHeadInspectionNavigationAdapter(IHeadInspectionMotion):
    def __init__(self, navigation: IPaintInspectionNavigation) -> None:
        self._navigation = navigation

    def move_to_inspection(
        self,
        target: HeadInspectionTarget,
        control: IHeadInspectionControl,
    ) -> HeadInspectionMoveResult:
        if control.should_stop():
            return HeadInspectionMoveCancelled()
        if control.pause_requested():
            return HeadInspectionMovePaused()

        def interrupted() -> bool:
            return control.should_stop() or control.pause_requested()

        reached = self._navigation.move_to_position(
            list(target.position),
            target.group_id.value,
            wait_cancelled=interrupted,
            velocity=target.velocity_percent,
            acceleration=target.acceleration_percent,
            motion_type=_MOTION_TYPES[target.motion_type],
            blendR=0.0,
        )
        if control.should_stop():
            return HeadInspectionMoveCancelled()
        if control.pause_requested():
            return HeadInspectionMovePaused()
        if not reached:
            return HeadInspectionMoveFailed(
                HeadInspectionFailure(
                    HeadInspectionFailureCode.INSPECTION_MOTION_FAILED,
                    f"Could not reach the configured '{target.group_id.value}' inspection position",
                )
            )
        return HeadInspectionPositionReached()
