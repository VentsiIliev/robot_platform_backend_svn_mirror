from src.robot_systems.paint_auto_dry.paint_robot_system import AutomaticDryerPaintRobotSystem
from src.robot_systems.paint_tray_dry.paint_robot_system import TrayDryerPaintRobotSystem
import os
import unittest
from unittest.mock import MagicMock, patch

from src.robot_systems.paint_auto_dry.bootstrap_provider import (
    create_bootstrap_provider as create_auto_dry_provider,
)
from src.robot_systems.paint.paint_robot_system import (
    PaintRobotSystem,
)
from src.robot_systems.paint.applications.paint_process_settings.view.paint_process_settings_schema import (
    build_process_groups,
)
from src.robot_systems.paint.processes.paint.config import (
    PaintDropoffConfig,
    PaintProcessConfig,
)
from src.robot_systems.paint.processes.paint.paint_process_config_service import (
    PaintProcessConfigService,
)
from src.robot_systems.paint_tray_dry.bootstrap_provider import (
    create_bootstrap_provider as create_tray_dry_provider,
)


class TestPaintProfiles(unittest.TestCase):
    def test_remote_support_screen_is_absent_from_all_paint_profiles(self):
        for system in (PaintRobotSystem, AutomaticDryerPaintRobotSystem, TrayDryerPaintRobotSystem):
            with self.subTest(system=system.__name__):
                names = {spec.name.lower() for spec in system.shell.applications}
                self.assertNotIn("remotesupport", names)
                self.assertNotIn("remotesupport", system.role_policy.protected_app_role_values)
                self.assertIn("softwareupdate", names)

    def test_fresh_tray_defaults_are_valid_without_changing_saved_values(self):
        from src.robot_systems.paint.component_ids import SettingsID
        from src.robot_systems.paint.processes.paint.paint_process_config_serializer import PaintProcessConfigSerializer

        serializer = next(spec.serializer for spec in TrayDryerPaintRobotSystem.settings_specs
                          if spec.name == SettingsID.PAINT_PROCESS_CONFIG)
        settings_service = MagicMock()
        settings_service.get.return_value = serializer.get_default()
        service = PaintProcessConfigService(settings_service, allowed_dropoff_strategies=("plate_layout",))
        self.assertEqual("plate_layout", service.get_snapshot().dropoff.strategy)
        saved = serializer.to_dict(serializer.get_default())
        saved["dropoff"]["strategy"] = "movement_group"
        self.assertEqual("movement_group", serializer.from_dict(saved).dropoff.strategy)
        self.assertEqual("movement_group", PaintProcessConfigSerializer().get_default().dropoff.strategy)

    def test_selects_automatic_dryer_profile(self):
        provider = create_auto_dry_provider()

        self.assertTrue(issubclass(provider.system_class, AutomaticDryerPaintRobotSystem))
        self.assertEqual(provider.system_class.metadata, AutomaticDryerPaintRobotSystem.metadata)

    def test_selects_tray_dryer_profile(self):
        provider = create_tray_dry_provider()

        self.assertTrue(issubclass(provider.system_class, TrayDryerPaintRobotSystem))
        self.assertEqual(provider.system_class.metadata, TrayDryerPaintRobotSystem.metadata)
        self.assertFalse(provider.system_class.ui_config.show_drying_mode_control)

    def test_automatic_dryer_keeps_mode_selection(self):
        provider = create_auto_dry_provider()

        self.assertTrue(provider.system_class.ui_config.show_drying_mode_control)

    def test_tray_dryer_only_allows_plate_layout_dropoff(self):
        self.assertEqual(
            TrayDryerPaintRobotSystem.allowed_dropoff_strategies,
            ("plate_layout",),
        )

        strategy_field = next(
            field
            for group in build_process_groups(
                TrayDryerPaintRobotSystem.allowed_dropoff_strategies
            )
            for field in group.fields
            if field.key == "dropoff_strategy"
        )
        self.assertEqual(strategy_field.choices, ["plate_layout"])
        self.assertEqual(strategy_field.default, "plate_layout")

    def test_all_paint_profiles_exclude_height_measurement(self):
        from src.engine.common_settings_ids import CommonSettingsID

        height_settings = {
            CommonSettingsID.HEIGHT_MEASURING_SETTINGS,
            CommonSettingsID.HEIGHT_MEASURING_CALIBRATION,
            CommonSettingsID.DEPTH_MAP_DATA,
        }
        systems = [PaintRobotSystem, AutomaticDryerPaintRobotSystem,
                   TrayDryerPaintRobotSystem, create_auto_dry_provider().system_class,
                   create_tray_dry_provider().system_class]
        for system in systems:
            with self.subTest(system=system.__name__):
                self.assertFalse(height_settings & {spec.name for spec in system.settings_specs})
                self.assertTrue(all(not frame.use_height_correction for frame in system.target_frames))
                self.assertTrue(all(not area.supports_height_mapping for area in system.work_areas))

    def test_tray_dryer_rejects_movement_group_dropoff_at_runtime(self):
        settings = MagicMock()
        settings.get.return_value = PaintProcessConfig(
            dropoff=PaintDropoffConfig(strategy="plate_layout")
        )
        service = PaintProcessConfigService(
            settings,
            allowed_dropoff_strategies=("plate_layout",),
        )

        with self.assertRaisesRegex(ValueError, "not available"):
            service.save(
                PaintProcessConfig(
                    dropoff=PaintDropoffConfig(strategy="movement_group")
                )
            )

        settings.save.assert_not_called()

    def test_profile_storage_is_isolated(self):
        automatic_root = AutomaticDryerPaintRobotSystem.storage_path()
        tray_root = TrayDryerPaintRobotSystem.storage_path()

        self.assertNotEqual(automatic_root, tray_root)
        self.assertTrue(automatic_root.endswith(os.path.join("paint_auto_dry", "storage")))
        self.assertTrue(tray_root.endswith(os.path.join("paint_tray_dry", "storage")))
        self.assertTrue(
            AutomaticDryerPaintRobotSystem.users_storage_path().startswith(automatic_root)
        )
        self.assertTrue(
            TrayDryerPaintRobotSystem.permissions_storage_path().startswith(tray_root)
        )

    def test_providers_resolve_installed_storage_in_their_own_system(self):
        with patch.dict(os.environ, {'ROBOT_PLATFORM_DATA_ROOT': '/tmp/paint-profile-test-data'}):
            for provider, system in [(create_auto_dry_provider(), 'paint_auto_dry'),
                                     (create_tray_dry_provider(), 'paint_tray_dry')]:
                self.assertEqual(provider.system_class.storage_path('settings'),
                                 f'/tmp/paint-profile-test-data/{system}/storage/settings')

if __name__ == "__main__":
    unittest.main()
