"""Explicit typed registration; no class names, reflection or dynamic imports."""

from collections.abc import Callable
from dataclasses import dataclass
from functools import partial

from src.robot_systems.paint.contracts.paint_head_check.errors import PaintHeadConfigurationError
from src.robot_systems.paint.contracts.paint_head_check.interfaces import IPaintHeadCheckPolicy
from src.robot_systems.paint.contracts.paint_head_check.models import (
    HeadCheckPolicyDescription,
    HeadCheckPolicyId,
)

from .scheduling import (
    EveryCycleHeadCheckPolicy,
    FirstCycleHeadCheckPolicy,
    FirstThenIntervalHeadCheckPolicy,
)

EVERY_CYCLE_POLICY = HeadCheckPolicyId("every_cycle")
FIRST_CYCLE_POLICY = HeadCheckPolicyId("first_cycle")
FIRST_THEN_INTERVAL_POLICY = HeadCheckPolicyId("first_then_interval")


@dataclass(frozen=True, slots=True)
class HeadCheckPolicyRegistration:
    description: HeadCheckPolicyDescription
    factory: Callable[[], IPaintHeadCheckPolicy]


class PaintHeadCheckPolicyRegistry:
    def __init__(self) -> None:
        self._registrations: dict[HeadCheckPolicyId, HeadCheckPolicyRegistration] = {}

    def register(self, registration: HeadCheckPolicyRegistration) -> None:
        identity = registration.description.policy_id
        if identity in self._registrations:
            raise PaintHeadConfigurationError(
                f"Head-check policy is already registered: {identity.value}",
            )
        self._registrations[identity] = registration

    def create(self, policy_id: HeadCheckPolicyId) -> IPaintHeadCheckPolicy:
        try:
            registration = self._registrations[policy_id]
        except KeyError as error:
            raise PaintHeadConfigurationError(
                f"Head-check policy is not registered: {policy_id.value}",
            ) from error
        return registration.factory()

    def descriptions(self) -> tuple[HeadCheckPolicyDescription, ...]:
        return tuple(item.description for item in self._registrations.values())


def build_head_check_policy_registry(interval_cycles: int) -> PaintHeadCheckPolicyRegistry:
    registry = PaintHeadCheckPolicyRegistry()
    registry.register(
        HeadCheckPolicyRegistration(
            HeadCheckPolicyDescription(EVERY_CYCLE_POLICY, "Every cycle", False),
            EveryCycleHeadCheckPolicy,
        )
    )
    registry.register(
        HeadCheckPolicyRegistration(
            HeadCheckPolicyDescription(FIRST_CYCLE_POLICY, "First cycle after Start", False),
            FirstCycleHeadCheckPolicy,
        )
    )
    registry.register(
        HeadCheckPolicyRegistration(
            HeadCheckPolicyDescription(
                FIRST_THEN_INTERVAL_POLICY,
                "First cycle, then every N cycles",
                True,
            ),
            partial(FirstThenIntervalHeadCheckPolicy, interval_cycles),
        )
    )
    return registry
