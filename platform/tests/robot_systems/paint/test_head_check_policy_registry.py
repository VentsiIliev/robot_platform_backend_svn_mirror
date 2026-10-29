"""A custom policy is registered without changing the coordinator or detector."""

import unittest

from src.robot_systems.paint.contracts.paint_head_check.errors import PaintHeadConfigurationError
from src.robot_systems.paint.contracts.paint_head_check.interfaces import IPaintHeadCheckPolicy
from src.robot_systems.paint.contracts.paint_head_check.models import (
    HeadCheckPolicyDescription,
    HeadCheckPolicyId,
    HeadCheckProgress,
    HeadCheckScheduleDecision,
)
from src.robot_systems.paint.paint_head_check.policy_registry import (
    EVERY_CYCLE_POLICY,
    FIRST_CYCLE_POLICY,
    FIRST_THEN_INTERVAL_POLICY,
    HeadCheckPolicyRegistration,
    build_head_check_policy_registry,
)


class CustomSchedule(IPaintHeadCheckPolicy):
    def evaluate(self, progress: HeadCheckProgress) -> HeadCheckScheduleDecision:
        return (
            HeadCheckScheduleDecision.DUE
            if progress.completed_workpieces in (0, 3, 8)
            else HeadCheckScheduleDecision.NOT_DUE
        )


class HeadCheckPolicyRegistryTests(unittest.TestCase):
    def test_registered_builtin_policies_receive_the_explicit_interval(self) -> None:
        registry = build_head_check_policy_registry(5)
        self.assertIs(
            HeadCheckScheduleDecision.DUE,
            registry.create(EVERY_CYCLE_POLICY).evaluate(HeadCheckProgress(2)),
        )
        self.assertIs(
            HeadCheckScheduleDecision.NOT_DUE,
            registry.create(FIRST_CYCLE_POLICY).evaluate(HeadCheckProgress(2)),
        )
        interval = registry.create(FIRST_THEN_INTERVAL_POLICY)
        self.assertIs(HeadCheckScheduleDecision.DUE, interval.evaluate(HeadCheckProgress(5)))
        self.assertIs(HeadCheckScheduleDecision.NOT_DUE, interval.evaluate(HeadCheckProgress(4)))

    def test_new_policy_registers_a_typed_identity_and_settings_descriptor(self) -> None:
        registry = build_head_check_policy_registry(5)
        identity = HeadCheckPolicyId("custom_schedule")
        descriptor = HeadCheckPolicyDescription(identity, "Custom schedule", False)
        registry.register(HeadCheckPolicyRegistration(descriptor, CustomSchedule))
        self.assertIn(descriptor, registry.descriptions())
        custom = registry.create(identity)
        self.assertIs(HeadCheckScheduleDecision.DUE, custom.evaluate(HeadCheckProgress(8)))
        self.assertIs(HeadCheckScheduleDecision.NOT_DUE, custom.evaluate(HeadCheckProgress(7)))

    def test_duplicate_or_unknown_policy_never_falls_back_to_a_builtin(self) -> None:
        registry = build_head_check_policy_registry(5)
        with self.assertRaises(PaintHeadConfigurationError):
            registry.create(HeadCheckPolicyId("not_registered"))
        with self.assertRaises(PaintHeadConfigurationError):
            registry.register(
                HeadCheckPolicyRegistration(
                    HeadCheckPolicyDescription(EVERY_CYCLE_POLICY, "Duplicate", False),
                    CustomSchedule,
                )
            )


if __name__ == "__main__":
    unittest.main()
