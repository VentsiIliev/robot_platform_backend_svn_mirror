"""Checks run before due cycles and never as a consequence of drop-off."""

import unittest

from src.robot_systems.paint.contracts.paint_head_check.errors import PaintHeadContractError
from src.robot_systems.paint.paint_head_check.scheduling import (
    DisabledHeadCheckPolicy,
    EveryCycleHeadCheckPolicy,
    FirstCycleHeadCheckPolicy,
    FirstThenIntervalHeadCheckPolicy,
)
from src.robot_systems.paint.paint_head_check.session import PaintHeadCheckSession


class HeadCheckSessionTests(unittest.TestCase):
    def test_interval_checks_before_workpieces_one_six_eleven_sixteen(self) -> None:
        session = PaintHeadCheckSession(FirstThenIntervalHeadCheckPolicy(5))
        checked = []
        for workpiece in range(1, 17):
            if session.check_before_cycle_due():
                checked.append(workpiece)
                session.mark_check_complete()
            self.assertFalse(session.check_before_cycle_due())
            session.record_completed_cycle()
        self.assertEqual([1, 6, 11, 16], checked)

    def test_every_cycle_requires_a_check_before_completion(self) -> None:
        session = PaintHeadCheckSession(EveryCycleHeadCheckPolicy())
        for _ in range(3):
            self.assertTrue(session.check_before_cycle_due())
            session.mark_check_complete()
            self.assertFalse(session.check_before_cycle_due())
            session.record_completed_cycle()
        self.assertEqual(3, session.progress.completed_workpieces)

    def test_first_only_does_not_repeat_on_subsequent_cycles_or_resume(self) -> None:
        session = PaintHeadCheckSession(FirstCycleHeadCheckPolicy())
        self.assertTrue(session.check_before_cycle_due())
        session.mark_check_complete()
        for _ in range(3):
            self.assertFalse(session.check_before_cycle_due())
            session.record_completed_cycle()
        self.assertTrue(PaintHeadCheckSession(FirstCycleHeadCheckPolicy()).check_before_cycle_due())

    def test_failed_or_paused_checks_remain_due_without_advancing_workpieces(self) -> None:
        session = PaintHeadCheckSession(EveryCycleHeadCheckPolicy())
        self.assertTrue(session.check_before_cycle_due())
        self.assertTrue(session.check_before_cycle_due())
        self.assertEqual(0, session.progress.completed_workpieces)
        session.mark_check_complete()
        self.assertFalse(session.check_before_cycle_due())
        self.assertEqual(0, session.progress.completed_workpieces)

    def test_a_required_check_cannot_be_bypassed_by_completing_a_cycle(self) -> None:
        session = PaintHeadCheckSession(EveryCycleHeadCheckPolicy())
        with self.assertRaises(PaintHeadContractError):
            session.record_completed_cycle()

    def test_disabled_policy_never_requires_an_inspection(self) -> None:
        session = PaintHeadCheckSession(DisabledHeadCheckPolicy())
        for _ in range(3):
            self.assertFalse(session.check_before_cycle_due())
            session.record_completed_cycle()


if __name__ == "__main__":
    unittest.main()
