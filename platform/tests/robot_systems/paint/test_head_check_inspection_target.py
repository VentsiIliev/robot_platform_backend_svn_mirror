"""The configured alignment group is mandatory; invalid targets cannot fall back."""

import unittest
from dataclasses import replace

from src.engine.robot.configuration.movement_group_settings import MovementGroupSettings
from src.engine.robot.configuration.robot_settings import MovementGroup
from src.robot_systems.paint.component_ids import MovementGroupID
from src.robot_systems.paint.contracts.paint_head_check.errors import (
    HeadInspectionFailureCode,
    PaintHeadInspectionTargetError,
)
from src.robot_systems.paint.contracts.paint_head_check.models import HeadInspectionMotionType
from src.robot_systems.paint.paint_head_check.adapters.inspection_target import (
    ShaftAlignmentInspectionTargetProvider,
)


class InspectionTargetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.group = MovementGroup(
            position="[10, 20, 30, 180, 0, 45]",
            velocity=20,
            acceleration=30,
            motion_type="ptp",
            has_trajectory_execution=True,
        )
        self.settings = MovementGroupSettings(
            {
                MovementGroupID.VERTICAL_SHAFT_ALIGNMENT.value: self.group,
            }
        )
        self.provider = ShaftAlignmentInspectionTargetProvider(self.get_settings)

    def get_settings(self) -> MovementGroupSettings:
        return self.settings

    def test_resolves_only_the_explicit_taught_values(self) -> None:
        result = self.provider.resolve()
        self.assertEqual((10, 20, 30, 180, 0, 45), result.position)
        self.assertEqual(20, result.velocity_percent)
        self.assertEqual(30, result.acceleration_percent)
        self.assertIs(MovementGroupID.VERTICAL_SHAFT_ALIGNMENT, result.group_id)
        self.assertIs(HeadInspectionMotionType.POINT_TO_POINT, result.motion_type)

    def test_missing_alignment_group_cannot_use_another_taught_group(self) -> None:
        self.settings = MovementGroupSettings({"Vertical Shaft": self.group})
        with self.assertRaises(PaintHeadInspectionTargetError) as raised:
            self.provider.resolve()
        self.assertIs(
            HeadInspectionFailureCode.INSPECTION_GROUP_MISSING,
            raised.exception.failure.code,
        )
        self.assertIn("Vertical Shaft Alignment", str(raised.exception))
        self.assertIn("Robot Settings", str(raised.exception))

    def test_missing_malformed_and_nonfinite_positions_are_rejected(self) -> None:
        invalid_positions = (
            None,
            "",
            "not-json",
            "{}",
            "[1,2,3]",
            "[1,2,3,4,5,6,7]",
            '[1,2,3,4,5,"6"]',
            "[true,2,3,4,5,6]",
            "[1,2,3,4,5,NaN]",
            "[1,2,3,4,5,Infinity]",
        )
        for position in invalid_positions:
            with self.subTest(position=position):
                self.settings.movement_groups[MovementGroupID.VERTICAL_SHAFT_ALIGNMENT.value] = (
                    replace(self.group, position=position)
                )
                with self.assertRaises(PaintHeadInspectionTargetError) as raised:
                    self.provider.resolve()
                self.assertIs(
                    HeadInspectionFailureCode.INSPECTION_POSITION_INVALID,
                    raised.exception.failure.code,
                )

    def test_zero_velocity_or_acceleration_cannot_use_a_default(self) -> None:
        cases = (
            (
                replace(self.group, velocity=0),
                HeadInspectionFailureCode.INSPECTION_VELOCITY_INVALID,
            ),
            (
                replace(self.group, acceleration=0),
                HeadInspectionFailureCode.INSPECTION_ACCELERATION_INVALID,
            ),
            (
                replace(self.group, velocity=101),
                HeadInspectionFailureCode.INSPECTION_VELOCITY_INVALID,
            ),
            (
                replace(self.group, acceleration=-1),
                HeadInspectionFailureCode.INSPECTION_ACCELERATION_INVALID,
            ),
        )
        for group, code in cases:
            with self.subTest(code=code, group=group):
                self.settings.movement_groups[MovementGroupID.VERTICAL_SHAFT_ALIGNMENT.value] = (
                    group
                )
                with self.assertRaises(PaintHeadInspectionTargetError) as raised:
                    self.provider.resolve()
                self.assertIs(code, raised.exception.failure.code)

    def test_disabled_execution_and_unknown_motion_type_are_rejected(self) -> None:
        cases = (
            (
                replace(self.group, has_trajectory_execution=False),
                HeadInspectionFailureCode.INSPECTION_MOVEMENT_DISABLED,
            ),
            (
                replace(self.group, motion_type="typo"),
                HeadInspectionFailureCode.INSPECTION_MOTION_TYPE_INVALID,
            ),
        )
        for group, code in cases:
            with self.subTest(code=code):
                self.settings.movement_groups[MovementGroupID.VERTICAL_SHAFT_ALIGNMENT.value] = (
                    group
                )
                with self.assertRaises(PaintHeadInspectionTargetError) as raised:
                    self.provider.resolve()
                self.assertIs(code, raised.exception.failure.code)

    def test_a_corrected_group_is_read_again_without_mutating_earlier_results(self) -> None:
        original = self.provider.resolve()
        self.settings.movement_groups[MovementGroupID.VERTICAL_SHAFT_ALIGNMENT.value] = replace(
            self.group,
            position="[100,200,300,180,0,90]",
            motion_type="linear",
        )
        updated = self.provider.resolve()
        self.assertEqual((10, 20, 30, 180, 0, 45), original.position)
        self.assertEqual((100, 200, 300, 180, 0, 90), updated.position)
        self.assertIs(HeadInspectionMotionType.LINEAR, updated.motion_type)

    def test_unexpected_settings_provider_errors_are_not_disguised_as_bad_configuration(
        self,
    ) -> None:
        def broken_settings() -> MovementGroupSettings:
            raise RuntimeError("unexpected settings repository failure")

        provider = ShaftAlignmentInspectionTargetProvider(broken_settings)
        with self.assertRaisesRegex(RuntimeError, "unexpected settings repository failure"):
            provider.resolve()


if __name__ == "__main__":
    unittest.main()
