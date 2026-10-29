"""Presentation/persistence keys stay outside typed policy decisions."""

from collections.abc import Mapping

from src.robot_systems.paint.contracts.paint_head_check.models import PaintHeadCheckConfiguration
from src.robot_systems.paint.paint_head_check.configuration import (
    head_check_from_dict,
    head_check_to_dict,
)


def head_check_to_flat(configuration: PaintHeadCheckConfiguration) -> dict[str, object]:
    return {f"head_check_{key}": value for key, value in head_check_to_dict(configuration).items()}


def head_check_from_flat(
    flat: Mapping[str, object],
    base: PaintHeadCheckConfiguration,
) -> PaintHeadCheckConfiguration:
    known = head_check_to_dict(base)
    supplied = {key: flat[f"head_check_{key}"] for key in known if f"head_check_{key}" in flat}
    return head_check_from_dict(supplied, default=base)
