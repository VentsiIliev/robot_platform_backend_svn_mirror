"""Persistence and settings conversion retain typed choices and safe migration defaults."""

import json
import unittest
from dataclasses import replace

from src.robot_systems.paint.applications.paint_process_settings.mapper import (
    PaintProcessSettingsMapper,
)
from src.robot_systems.paint.contracts.paint_head_check.errors import PaintHeadConfigurationError
from src.robot_systems.paint.contracts.paint_head_check.models import PaintHeadAction
from src.robot_systems.paint.paint_head_check.configuration import (
    default_head_check_configuration,
    head_check_from_dict,
    head_check_to_dict,
)
from src.robot_systems.paint.paint_head_check.policy_registry import FIRST_THEN_INTERVAL_POLICY
from src.robot_systems.paint.processes.paint.configuration.models import PaintProcessConfig
from src.robot_systems.paint.processes.paint.configuration.serializer import (
    PaintProcessConfigSerializer,
)


class HeadCheckSettingsTests(unittest.TestCase):
    def test_existing_settings_load_off_with_configurable_stop_responses(self) -> None:
        configuration = PaintProcessConfigSerializer().from_dict({}).head_check
        self.assertFalse(configuration.enabled)
        self.assertEqual(1.0, configuration.timeout_seconds)
        self.assertTrue(configuration.report_until_confirmed)
        self.assertIs(PaintHeadAction.STOP, configuration.state_reactions.missing)
        self.assertIs(PaintHeadAction.STOP, configuration.state_reactions.misaligned)
        self.assertIs(PaintHeadAction.CONTINUE, configuration.state_reactions.present)
        self.assertIs(PaintHeadAction.REPORT_ONLY, configuration.failure_action)

    def test_root_json_round_trip_reconstructs_ids_and_actions(self) -> None:
        original = replace(
            PaintProcessConfig(),
            head_check=replace(
                default_head_check_configuration(),
                enabled=True,
                policy_id=FIRST_THEN_INTERVAL_POLICY,
                interval_cycles=5,
                timeout_seconds=2.5,
                failure_action=PaintHeadAction.REJECT,
            ),
        )
        serializer = PaintProcessConfigSerializer()
        payload = json.loads(json.dumps(serializer.to_dict(original)))
        self.assertEqual("first_then_interval", payload["head_check"]["policy_id"])
        self.assertEqual("reject", payload["head_check"]["failure_action"])
        self.assertEqual(original, serializer.from_dict(payload))

    def test_settings_mapper_round_trips_all_head_check_fields(self) -> None:
        base = PaintProcessConfig()
        flat = PaintProcessSettingsMapper.to_flat_dict(base)
        flat.update(
            {
                "head_check_enabled": True,
                "head_check_policy_id": FIRST_THEN_INTERVAL_POLICY.value,
                "head_check_interval_cycles": 5,
                "head_check_timeout_seconds": 3.0,
                "head_check_missing_action": PaintHeadAction.PAUSE.value,
                "head_check_unknown_action": PaintHeadAction.RETRY.value,
            }
        )
        converted = PaintProcessSettingsMapper.from_flat_dict(flat, base)
        self.assertTrue(converted.head_check.enabled)
        self.assertEqual(FIRST_THEN_INTERVAL_POLICY, converted.head_check.policy_id)
        self.assertEqual(5, converted.head_check.interval_cycles)
        self.assertEqual(3.0, converted.head_check.timeout_seconds)
        self.assertIs(PaintHeadAction.PAUSE, converted.head_check.state_reactions.missing)
        self.assertIs(PaintHeadAction.RETRY, converted.head_check.state_reactions.unknown)
        restored = PaintProcessSettingsMapper.to_flat_dict(converted)
        for key, value in flat.items():
            if key.startswith("head_check_"):
                self.assertEqual(value, restored[key])

    def test_invalid_json_does_not_coerce_or_fall_back(self) -> None:
        cases = (
            None,
            [],
            {"enabled": "false"},
            {"interval_cycles": True},
            {"interval_cycles": 0},
            {"timeout_seconds": -1},
            {"timeout_seconds": float("inf")},
            {"timeout_seconds": "1"},
            {"unknown_action": "ignore_typo"},
            {"timeout_action": "retry"},
            {"unsupported": 1},
        )
        for invalid in cases:
            with self.subTest(raw=invalid):
                with self.assertRaises(PaintHeadConfigurationError):
                    head_check_from_dict(invalid)

    def test_partial_updates_preserve_explicit_base_settings(self) -> None:
        base = replace(default_head_check_configuration(), timeout_seconds=4.0)
        restored = head_check_from_dict({"enabled": True}, default=base)
        self.assertEqual(4.0, restored.timeout_seconds)
        self.assertTrue(restored.enabled)
        self.assertEqual(base.policy_id, restored.policy_id)
        self.assertEqual("continue", head_check_to_dict(restored)["present_action"])


if __name__ == "__main__":
    unittest.main()
