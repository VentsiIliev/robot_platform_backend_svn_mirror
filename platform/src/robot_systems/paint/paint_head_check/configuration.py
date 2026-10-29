"""Typed run settings and explicit JSON/UI boundary conversion."""

from collections.abc import Mapping

from src.robot_systems.paint.contracts.paint_head_check.errors import PaintHeadConfigurationError
from src.robot_systems.paint.contracts.paint_head_check.models import (
    HeadCheckPolicyId,
    PaintHeadAction,
    PaintHeadCheckConfiguration,
    PaintHeadStateReactions,
)

from .policy_registry import EVERY_CYCLE_POLICY


def default_head_check_configuration() -> PaintHeadCheckConfiguration:
    report = PaintHeadAction.REPORT_ONLY
    return PaintHeadCheckConfiguration(
        enabled=False,
        policy_id=EVERY_CYCLE_POLICY,
        interval_cycles=1,
        timeout_seconds=1.0,
        state_reactions=PaintHeadStateReactions(
            present=PaintHeadAction.CONTINUE,
            missing=PaintHeadAction.STOP,
            misaligned=PaintHeadAction.STOP,
            unknown=report,
        ),
        failure_action=report,
        timeout_action=report,
        report_until_confirmed=True,
    )


def head_check_to_dict(configuration: PaintHeadCheckConfiguration) -> dict[str, object]:
    return {
        "enabled": configuration.enabled,
        "policy_id": configuration.policy_id.value,
        "interval_cycles": configuration.interval_cycles,
        "timeout_seconds": configuration.timeout_seconds,
        "present_action": configuration.state_reactions.present.value,
        "missing_action": configuration.state_reactions.missing.value,
        "misaligned_action": configuration.state_reactions.misaligned.value,
        "unknown_action": configuration.state_reactions.unknown.value,
        "failure_action": configuration.failure_action.value,
        "timeout_action": configuration.timeout_action.value,
        "report_until_confirmed": configuration.report_until_confirmed,
    }


def head_check_from_dict(
    raw: object,
    *,
    default: PaintHeadCheckConfiguration | None = None,
) -> PaintHeadCheckConfiguration:
    if not isinstance(raw, Mapping):
        raise PaintHeadConfigurationError("Paint-head check settings must be a JSON object")
    values = head_check_to_dict(default or default_head_check_configuration())
    # Discard the retired return-route setting when loading an earlier saved file.
    legacy_return_key = "check_after_final_dropoff"
    if legacy_return_key in raw:
        _boolean(raw[legacy_return_key])
    unknown = set(raw) - set(values) - {legacy_return_key}
    if unknown:
        raise PaintHeadConfigurationError(f"Unsupported paint-head check setting(s): {unknown}")
    values.update({key: value for key, value in raw.items() if key != legacy_return_key})
    policy_id = values["policy_id"]
    if not isinstance(policy_id, str):
        raise PaintHeadConfigurationError(
            "Paint-head check policy ID must be a string at the JSON boundary"
        )
    return PaintHeadCheckConfiguration(
        enabled=_boolean(values["enabled"]),
        policy_id=HeadCheckPolicyId(policy_id),
        interval_cycles=_integer(values["interval_cycles"]),
        timeout_seconds=_number(values["timeout_seconds"]),
        state_reactions=PaintHeadStateReactions(
            _action(values["present_action"]),
            _action(values["missing_action"]),
            _action(values["misaligned_action"]),
            _action(values["unknown_action"]),
        ),
        failure_action=_action(values["failure_action"]),
        timeout_action=_action(values["timeout_action"]),
        report_until_confirmed=_boolean(values["report_until_confirmed"]),
    )


def _boolean(value: object) -> bool:
    if type(value) is not bool:
        raise PaintHeadConfigurationError("Paint-head check switches require boolean values")
    return value


def _integer(value: object) -> int:
    if type(value) is not int:
        raise PaintHeadConfigurationError("Paint-head check interval requires an integer")
    return value


def _number(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise PaintHeadConfigurationError("Paint-head check timeout requires a number")
    try:
        return float(value)
    except OverflowError as error:
        raise PaintHeadConfigurationError("Paint-head check timeout must be finite") from error


def _action(value: object) -> PaintHeadAction:
    if not isinstance(value, str):
        raise PaintHeadConfigurationError("Paint-head response requires a registered action ID")
    try:
        return PaintHeadAction(value)
    except ValueError as error:
        raise PaintHeadConfigurationError(f"Unknown paint-head response: {value}") from error
