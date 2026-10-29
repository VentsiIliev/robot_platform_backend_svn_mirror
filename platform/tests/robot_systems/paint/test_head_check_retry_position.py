"""The retry shortcut requires a retained stop and fresh feedback within explicit limits."""

import logging
import unittest
from collections import deque
from dataclasses import replace

from src.robot_systems.paint.component_ids import MovementGroupID
from src.robot_systems.paint.contracts.paint_head_check.models import (
    HeadInspectionMotionType,
    HeadInspectionPositionTolerance,
    HeadInspectionTarget,
)
from src.robot_systems.paint.paint_head_check.adapters.retry_position import (
    VerifiedInspectionRetryPosition,
)


class FakeNavigation:
    def __init__(self) -> None:
        self.pose: list[float] | None = [1.0, 2.0, 3.0, 180.0, 0.0, 0.0]
        self.reads: list[tuple[str, bool]] = []
        self.observed: list[str] = []
        self.error: OSError | None = None

    def get_current_observer_position(
        self, group_name: str, *, fresh: bool = False
    ) -> list[float] | None:
        self.reads.append((group_name, fresh))
        if self.error is not None:
            raise self.error
        return self.pose

    def mark_group_observed_area_verified(self, group_name: str) -> None:
        self.observed.append(group_name)


class FakeRobot:
    def __init__(self) -> None:
        self.status: object = {"is_executing": False}
        self.statuses: deque[object] = deque()
        self.tool_accepted = True
        self.user_accepted = True
        self.frames: list[tuple[str, int]] = []

    def get_execution_status(self) -> object:
        return self.statuses.popleft() if self.statuses else self.status

    def set_active_tool(self, tool: int) -> bool:
        self.frames.append(("tool", tool))
        return self.tool_accepted

    def set_active_workobject(self, user: int) -> bool:
        self.frames.append(("user", user))
        return self.user_accepted


class HeadCheckRetryPositionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.navigation = FakeNavigation()
        self.robot = FakeRobot()
        self.frame = (1, 1)
        self.target = HeadInspectionTarget(
            MovementGroupID.VERTICAL_SHAFT_ALIGNMENT,
            (1, 2, 3, 180, 0, 0),
            20,
            30,
            HeadInspectionMotionType.POINT_TO_POINT,
        )
        self.guard = VerifiedInspectionRetryPosition(
            self.navigation,
            self.robot,
            self.reference_frame,
            HeadInspectionPositionTolerance(0.5, 0.2),
            logging.getLogger(__name__),
        )

    def reference_frame(self) -> tuple[int, int]:
        return self.frame

    def test_no_previous_inspection_stop_means_no_shortcut_or_feedback_reads(self) -> None:
        self.assertFalse(self.guard.try_reuse(self.target))
        self.assertEqual([], self.navigation.reads)
        self.assertEqual([], self.robot.frames)

    def test_stationary_retry_uses_fresh_pose_and_the_taught_frame(self) -> None:
        self.guard.remember_stop(self.target)
        self.navigation.pose = [1.3, 2.0, 3.0, -179.9, 0.0, 0.0]
        self.assertTrue(self.guard.try_reuse(self.target))
        self.assertEqual(
            [(MovementGroupID.VERTICAL_SHAFT_ALIGNMENT.value, True)] * 2, self.navigation.reads
        )
        self.assertEqual([("tool", 1), ("user", 1)] * 2, self.robot.frames)
        self.assertEqual([MovementGroupID.VERTICAL_SHAFT_ALIGNMENT.value], self.navigation.observed)

    def test_translation_and_rotation_outside_limits_invalidate_the_candidate(self) -> None:
        for pose in ([1.501, 2, 3, 180, 0, 0], [1, 2, 3, 180, 0.201, 0], [1.4, 2.4, 3, 180, 0, 0]):
            with self.subTest(pose=pose):
                self.navigation.pose = list(self.target.position)
                self.guard.remember_stop(self.target)
                self.navigation.pose = pose
                self.assertFalse(self.guard.try_reuse(self.target))
                self.navigation.pose = list(self.target.position)
                self.assertFalse(self.guard.try_reuse(self.target))

    def test_drift_from_the_retained_pose_also_requires_normal_startup(self) -> None:
        self.navigation.pose = [1.49, 2, 3, 180, 0, 0]
        self.guard.remember_stop(self.target)
        self.navigation.pose = [0.51, 2, 3, 180, 0, 0]
        self.assertFalse(self.guard.try_reuse(self.target))

    def test_changed_target_or_reference_frame_cannot_reuse_a_previous_stop(self) -> None:
        self.guard.remember_stop(self.target)
        self.assertFalse(self.guard.try_reuse(replace(self.target, position=(1, 2, 4, 180, 0, 0))))
        self.guard.remember_stop(self.target)
        self.frame = (2, 1)
        count = len(self.navigation.reads)
        self.assertFalse(self.guard.try_reuse(self.target))
        self.assertEqual(count, len(self.navigation.reads))

    def test_active_or_unknown_execution_and_rejected_frame_activation_prevent_reuse(self) -> None:
        for status in (
            None,
            {},
            {"is_executing": True},
            {"is_executing": False, "queued": True},
            {"is_executing": False, "ordered_motion_chain": {"state": "moving"}},
        ):
            with self.subTest(status=status):
                self.robot.status = {"is_executing": False}
                self.guard.remember_stop(self.target)
                self.robot.status = status
                self.assertFalse(self.guard.try_reuse(self.target))
        self.robot.status = {"is_executing": False}
        self.guard.remember_stop(self.target)
        self.robot.tool_accepted = False
        self.assertFalse(self.guard.try_reuse(self.target))

    def test_motion_starting_during_fresh_read_cannot_be_accepted(self) -> None:
        self.guard.remember_stop(self.target)
        self.robot.statuses = deque([{"is_executing": False}, {"is_executing": True}])
        self.assertFalse(self.guard.try_reuse(self.target))

    def test_bad_or_unavailable_pose_never_falls_back_to_cached_feedback(self) -> None:
        for pose in (
            None,
            [],
            [1, 2, 3, 180, 0],
            [float("nan"), 2, 3, 180, 0, 0],
            [True, 2, 3, 180, 0, 0],
        ):
            with self.subTest(pose=pose):
                self.navigation.pose = list(self.target.position)
                self.guard.remember_stop(self.target)
                self.navigation.pose = pose
                self.assertFalse(self.guard.try_reuse(self.target))
        self.navigation.pose = list(self.target.position)
        self.guard.remember_stop(self.target)
        self.navigation.error = OSError("feedback unavailable")
        with self.assertLogs(__name__, level="WARNING"):
            self.assertFalse(self.guard.try_reuse(self.target))

    def test_discarding_a_position_does_not_access_hardware(self) -> None:
        self.guard.remember_stop(self.target)
        count = len(self.navigation.reads)
        self.guard.invalidate()
        self.assertFalse(self.guard.try_reuse(self.target))
        self.assertEqual(count, len(self.navigation.reads))


if __name__ == "__main__":
    unittest.main()
