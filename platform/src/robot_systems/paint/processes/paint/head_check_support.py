"""Typed adaptation between inspection contracts and existing paint execution."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.robot_systems.paint.contracts.next_cycle_target import NextCycleTarget
from src.robot_systems.paint.contracts.paint_head_check.errors import (
    HeadInspectionFailure,
    HeadInspectionFailureCode,
)
from src.robot_systems.paint.contracts.paint_head_check.interfaces import IHeadInspectionControl
from src.robot_systems.paint.contracts.paint_head_check.results import (
    HeadCheckEvidence,
    HeadInspectionMoveCancelled,
    HeadInspectionMoveFailed,
    HeadInspectionMovePaused,
    HeadInspectionMoveResult,
    HeadInspectionPositionReached,
)
from src.robot_systems.paint.paint_head_check.adapters.navigation import IPaintInspectionNavigation
from src.robot_systems.paint.processes.paint.results import (
    PaintFailure,
    PaintFailureCode,
    PaintOperationError,
    PaintOperationResult,
    PaintOutcome,
)

if TYPE_CHECKING:
    from src.robot_systems.paint.processes.paint.workflow.context import PaintExecutionContext


@dataclass(frozen=True, kw_only=True)
class PaintHeadCheckFailure(PaintFailure):
    head_check_failure: HeadInspectionFailure


@dataclass(frozen=True, kw_only=True)
class PaintHeadCheckStopResult(PaintOperationResult):
    head_check_evidence: HeadCheckEvidence


def head_check_stopped(evidence: HeadCheckEvidence) -> PaintHeadCheckStopResult:
    message = (
        f"Paint-head check stopped painting: {evidence.message}"
        if isinstance(evidence, HeadInspectionFailure)
        else f"Paint-head check stopped painting: {evidence.state.name}"
    )
    return PaintHeadCheckStopResult(
        outcome=PaintOutcome.HEAD_CHECK_STOPPED,
        message=message,
        head_check_evidence=evidence,
    )


def head_check_failure(evidence: HeadCheckEvidence) -> PaintHeadCheckFailure:
    failure = (
        evidence
        if isinstance(evidence, HeadInspectionFailure)
        else HeadInspectionFailure(
            HeadInspectionFailureCode.STATE_REJECTED,
            f"Paint-head inspection rejected state {evidence.state.name}: {evidence.reason.name}",
        )
    )
    return PaintHeadCheckFailure(
        code=PaintFailureCode.HEAD_CHECK,
        stage=PaintFailureCode.HEAD_CHECK.value,
        message=failure.message,
        head_check_failure=failure,
    )


def head_check_failed(evidence: HeadCheckEvidence) -> PaintOperationResult:
    failure = head_check_failure(evidence)
    return PaintOperationResult(PaintOutcome.FAILED, failure.message, failure)


def head_check_error(evidence: HeadCheckEvidence) -> PaintOperationError:
    return PaintOperationError(head_check_failure(evidence))


class PaintHeadWorkflowControl(IHeadInspectionControl):
    def __init__(self, context: PaintExecutionContext) -> None:
        self._context = context

    def should_stop(self) -> bool:
        return self._context.should_stop()

    def pause_requested(self) -> bool:
        return not self._context.run_allowed.is_set() or self._context.control.pause_requested()


class PaintHeadReturnRoute:
    """Return through the public navigator after inspection, without substituting poses."""

    def __init__(
        self,
        navigation: IPaintInspectionNavigation,
        target_provider: Callable[[], NextCycleTarget | None],
    ) -> None:
        self._navigation = navigation
        self._target_provider = target_provider

    def move(self, control: IHeadInspectionControl) -> HeadInspectionMoveResult:
        if control.should_stop():
            return HeadInspectionMoveCancelled()
        if control.pause_requested():
            return HeadInspectionMovePaused()
        try:
            target = self._target_provider()
        except (KeyError, ValueError) as error:
            return HeadInspectionMoveFailed(
                HeadInspectionFailure(
                    HeadInspectionFailureCode.RETURN_TARGET_INVALID,
                    f"Paint-head inspection return target is invalid: {error}",
                )
            )
        if target is None:
            return HeadInspectionMoveFailed(
                HeadInspectionFailure(
                    HeadInspectionFailureCode.RETURN_TARGET_INVALID,
                    "Paint-head inspection requires a configured production start target for return",
                )
            )

        def interrupted() -> bool:
            return control.should_stop() or control.pause_requested()

        reached = self._navigation.move_to_position(
            list(target.position),
            target.group_id,
            wait_cancelled=interrupted,
            velocity=target.velocity_percent,
            acceleration=target.acceleration_percent,
            motion_type=target.motion_type.value,
            blendR=0.0,
        )
        if control.should_stop():
            return HeadInspectionMoveCancelled()
        if control.pause_requested():
            return HeadInspectionMovePaused()
        if not reached:
            return HeadInspectionMoveFailed(
                HeadInspectionFailure(
                    HeadInspectionFailureCode.RETURN_MOTION_FAILED,
                    f"Paint-head inspection finished, but return to '{target.group_id}' failed",
                )
            )
        return HeadInspectionPositionReached()
