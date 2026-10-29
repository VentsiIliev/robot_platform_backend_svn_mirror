"""Scheduling and reactions must work without a detector or runtime process."""

import subprocess
import sys
import unittest
from dataclasses import replace
from pathlib import Path

from src.robot_systems.paint.contracts.paint_head_check.errors import (
    HeadInspectionFailure,
    HeadInspectionFailureCode,
    PaintHeadConfigurationError,
    PaintHeadContractError,
)
from src.robot_systems.paint.contracts.paint_head_check.interfaces import (
    IPaintHeadCheckPolicy,
    IPaintHeadReactionPolicy,
)
from src.robot_systems.paint.contracts.paint_head_check.models import (
    HeadCheckContext,
    HeadCheckProgress,
    HeadCheckScheduleDecision,
    PaintHeadAction,
    PaintHeadObservation,
    PaintHeadObservationReason,
    PaintHeadState,
    PaintHeadStateReactions,
)
from src.robot_systems.paint.contracts.paint_head_check.results import (
    ContinuePainting,
    HeadReactionDecision,
    PauseForOperator,
    RejectPainting,
    RetryObservation,
    StopPainting,
)
from src.robot_systems.paint.paint_head_check.reactions import ConfiguredPaintHeadReactionPolicy
from src.robot_systems.paint.paint_head_check.scheduling import (
    DisabledHeadCheckPolicy,
    EveryCycleHeadCheckPolicy,
    FirstCycleHeadCheckPolicy,
    FirstThenIntervalHeadCheckPolicy,
)


def observation(
    state: PaintHeadState,
    *,
    reason: PaintHeadObservationReason = PaintHeadObservationReason.INSUFFICIENT_EVIDENCE,
) -> PaintHeadObservation:
    return PaintHeadObservation(
        state=state,
        observed_state=state,
        reason=reason,
        frame_sequence=1,
        frame_captured_at=10.0,
        frame_received_at=10.0,
        evaluated_at=10.1,
        calibration_revision=1,
        alignment=None,
        held_warning=False,
    )


def context() -> HeadCheckContext:
    return HeadCheckContext(HeadCheckProgress(0), 1, 0.1, None)


class HeadCheckSchedulingTests(unittest.TestCase):
    @staticmethod
    def due_workpieces(policy: IPaintHeadCheckPolicy, total: int) -> list[int]:
        return [
            completed + 1
            for completed in range(total)
            if policy.evaluate(HeadCheckProgress(completed)) is HeadCheckScheduleDecision.DUE
        ]

    def test_every_cycle_and_first_only_have_distinct_schedules(self) -> None:
        self.assertEqual(
            list(range(1, 12)),
            self.due_workpieces(EveryCycleHeadCheckPolicy(), 11),
        )
        self.assertEqual([1], self.due_workpieces(FirstCycleHeadCheckPolicy(), 11))

    def test_disabled_policy_never_schedules_a_check(self) -> None:
        self.assertEqual([], self.due_workpieces(DisabledHeadCheckPolicy(), 20))

    def test_interval_is_anchored_to_first_workpiece(self) -> None:
        self.assertEqual(
            [1, 6, 11, 16],
            self.due_workpieces(FirstThenIntervalHeadCheckPolicy(5), 16),
        )
        self.assertEqual(
            list(range(1, 7)),
            self.due_workpieces(FirstThenIntervalHeadCheckPolicy(1), 6),
        )

    def test_repeated_attempts_do_not_consume_a_due_check(self) -> None:
        for policy in (FirstCycleHeadCheckPolicy(), FirstThenIntervalHeadCheckPolicy(5)):
            with self.subTest(policy=type(policy)):
                progress = HeadCheckProgress(0)
                self.assertEqual(
                    [HeadCheckScheduleDecision.DUE] * 3,
                    [policy.evaluate(progress) for _ in range(3)],
                )

    def test_a_new_run_uses_new_progress_without_mutating_the_policy(self) -> None:
        policy = FirstCycleHeadCheckPolicy()
        self.assertIs(
            policy.evaluate(HeadCheckProgress(3)),
            HeadCheckScheduleDecision.NOT_DUE,
        )
        self.assertIs(policy.evaluate(HeadCheckProgress(0)), HeadCheckScheduleDecision.DUE)

    def test_invalid_intervals_raise_a_typed_configuration_error(self) -> None:
        for invalid in (0, -1):
            with self.subTest(interval=invalid):
                with self.assertRaises(PaintHeadConfigurationError) as raised:
                    FirstThenIntervalHeadCheckPolicy(invalid)
                self.assertIs(
                    raised.exception.failure.code,
                    HeadInspectionFailureCode.CONFIGURATION_INVALID,
                )

    def test_negative_progress_is_a_contract_failure(self) -> None:
        with self.assertRaises(PaintHeadContractError):
            HeadCheckProgress(-1)


class HeadCheckReactionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = ConfiguredPaintHeadReactionPolicy(
            PaintHeadStateReactions(
                present=PaintHeadAction.CONTINUE,
                missing=PaintHeadAction.PAUSE,
                misaligned=PaintHeadAction.REJECT,
                unknown=PaintHeadAction.RETRY,
            ),
            failure_action=PaintHeadAction.PAUSE,
            timeout_action=PaintHeadAction.REJECT,
        )

    def test_each_state_has_its_own_response(self) -> None:
        cases = (
            (PaintHeadState.PRESENT, ContinuePainting),
            (PaintHeadState.MISSING, PauseForOperator),
            (PaintHeadState.MISALIGNED, RejectPainting),
            (PaintHeadState.UNKNOWN, RetryObservation),
        )
        for state, expected in cases:
            with self.subTest(state=state):
                self.assertIsInstance(
                    self.policy.on_observation(observation(state), context()), expected
                )

    def test_observed_presence_does_not_override_unconfirmed_status(self) -> None:
        unconfirmed = replace(
            observation(PaintHeadState.UNKNOWN),
            observed_state=PaintHeadState.PRESENT,
            reason=PaintHeadObservationReason.CONFIRMING_STATUS,
        )
        self.assertIsInstance(self.policy.on_observation(unconfirmed, context()), RetryObservation)

    def test_held_misalignment_uses_the_confirmed_warning(self) -> None:
        held = replace(
            observation(PaintHeadState.MISALIGNED),
            observed_state=PaintHeadState.UNKNOWN,
            reason=PaintHeadObservationReason.RECHECKING_POSITION,
            held_warning=True,
        )
        self.assertIsInstance(self.policy.on_observation(held, context()), RejectPainting)

    def test_actions_are_configurable_for_every_state(self) -> None:
        cases = (
            (PaintHeadAction.CONTINUE, ContinuePainting),
            (PaintHeadAction.RETRY, RetryObservation),
            (PaintHeadAction.PAUSE, PauseForOperator),
            (PaintHeadAction.STOP, StopPainting),
            (PaintHeadAction.REJECT, RejectPainting),
        )
        for action, expected in cases:
            policy = ConfiguredPaintHeadReactionPolicy(
                PaintHeadStateReactions(action, action, action, action),
                failure_action=action,
                timeout_action=action,
            )
            for state in PaintHeadState:
                with self.subTest(action=action, state=state):
                    self.assertIsInstance(
                        policy.on_observation(observation(state), context()), expected
                    )

    def test_timeout_and_camera_failure_have_separate_responses(self) -> None:
        for code in HeadInspectionFailureCode:
            with self.subTest(code=code):
                # A misleading message cannot affect a typed reaction.
                failure = HeadInspectionFailure(code, "Head is present and aligned")
                expected = (
                    RejectPainting
                    if code is HeadInspectionFailureCode.TIMEOUT
                    else PauseForOperator
                )
                self.assertIsInstance(self.policy.on_failure(failure, context()), expected)


class LowContrastRetryPolicy(IPaintHeadReactionPolicy):
    """A custom policy uses domain reasons without changing built-in policies."""

    def on_observation(
        self,
        observation: PaintHeadObservation,
        context: HeadCheckContext,
    ) -> HeadReactionDecision:
        if observation.reason is PaintHeadObservationReason.LOW_CONTRAST:
            return RetryObservation()
        return RejectPainting()

    def on_failure(
        self,
        failure: HeadInspectionFailure,
        context: HeadCheckContext,
    ) -> HeadReactionDecision:
        return RejectPainting()


class HeadCheckIsolationTests(unittest.TestCase):
    def test_custom_policy_uses_domain_values_without_a_detector(self) -> None:
        policy: IPaintHeadReactionPolicy = LowContrastRetryPolicy()
        low_contrast = observation(
            PaintHeadState.UNKNOWN,
            reason=PaintHeadObservationReason.LOW_CONTRAST,
        )
        self.assertIsInstance(policy.on_observation(low_contrast, context()), RetryObservation)
        self.assertIsInstance(
            policy.on_observation(observation(PaintHeadState.MISSING), context()),
            RejectPainting,
        )

    def test_policies_import_without_loading_detector_or_platform_runtime(self) -> None:
        root = Path(__file__).resolve().parents[3]
        code = """
import sys
from src.robot_systems.paint.paint_head_check import scheduling, reactions
for name in sys.modules:
    assert not name.startswith((
        'src.robot_systems.paint.paint_head_detection',
        'src.robot_systems.paint.processes',
        'src.engine', 'PyQt6', 'cv2', 'numpy',
    )), name
"""
        result = subprocess.run(
            [sys.executable, "-B", "-c", code],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)


if __name__ == "__main__":
    unittest.main()
