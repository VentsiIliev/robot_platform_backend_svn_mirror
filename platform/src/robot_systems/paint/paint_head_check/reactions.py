"""Configurable typed responses; this module performs no workflow side effects."""

from typing import assert_never

from src.robot_systems.paint.contracts.paint_head_check.errors import (
    HeadInspectionFailure,
    HeadInspectionFailureCode,
    PaintHeadConfigurationError,
)
from src.robot_systems.paint.contracts.paint_head_check.interfaces import IPaintHeadReactionPolicy
from src.robot_systems.paint.contracts.paint_head_check.models import (
    HeadCheckContext,
    PaintHeadAction,
    PaintHeadObservation,
    PaintHeadState,
    PaintHeadStateReactions,
)
from src.robot_systems.paint.contracts.paint_head_check.results import (
    ContinuePainting,
    HeadReactionDecision,
    PauseForOperator,
    RejectPainting,
    ReportOnly,
    RetryObservation,
    StopPainting,
)


class ConfiguredPaintHeadReactionPolicy(IPaintHeadReactionPolicy):
    """All actions are explicit configuration, without hidden operational defaults."""

    def __init__(
        self,
        state_reactions: PaintHeadStateReactions,
        *,
        failure_action: PaintHeadAction,
        timeout_action: PaintHeadAction,
        report_until_confirmed: bool | None = None,
    ) -> None:
        if not isinstance(failure_action, PaintHeadAction):
            raise PaintHeadConfigurationError("Inspection failure response requires a typed action")
        if not isinstance(timeout_action, PaintHeadAction):
            raise PaintHeadConfigurationError("Inspection timeout response requires a typed action")
        self._state_reactions = state_reactions
        self._failure_action = failure_action
        self._timeout_action = timeout_action
        reports = PaintHeadAction.REPORT_ONLY in (
            state_reactions.present,
            state_reactions.missing,
            state_reactions.misaligned,
            state_reactions.unknown,
            failure_action,
            timeout_action,
        )
        if reports and type(report_until_confirmed) is not bool:
            raise PaintHeadConfigurationError(
                "Reporting-only reactions require an explicit confirmation preference",
            )
        self._report_until_confirmed = report_until_confirmed is True

    def on_observation(
        self,
        observation: PaintHeadObservation,
        context: HeadCheckContext,
    ) -> HeadReactionDecision:
        match observation.state:
            case PaintHeadState.PRESENT:
                action = self._state_reactions.present
            case PaintHeadState.MISSING:
                action = self._state_reactions.missing
            case PaintHeadState.MISALIGNED:
                action = self._state_reactions.misaligned
            case PaintHeadState.UNKNOWN:
                action = self._state_reactions.unknown
            case _ as unreachable:
                assert_never(unreachable)
        return _decision(action, await_confirmation=self._report_until_confirmed)

    def on_failure(
        self,
        failure: HeadInspectionFailure,
        context: HeadCheckContext,
    ) -> HeadReactionDecision:
        action = (
            self._timeout_action
            if failure.code is HeadInspectionFailureCode.TIMEOUT
            else self._failure_action
        )
        return _decision(action)


def _decision(
    action: PaintHeadAction,
    *,
    await_confirmation: bool = False,
) -> HeadReactionDecision:
    match action:
        case PaintHeadAction.REPORT_ONLY:
            return ReportOnly(await_confirmation)
        case PaintHeadAction.CONTINUE:
            return ContinuePainting()
        case PaintHeadAction.RETRY:
            return RetryObservation()
        case PaintHeadAction.PAUSE:
            return PauseForOperator()
        case PaintHeadAction.STOP:
            return StopPainting()
        case PaintHeadAction.REJECT:
            return RejectPainting()
        case _ as unreachable:
            assert_never(unreachable)
