from src.robot_systems.paint_auto_dry.paint_robot_system import AutomaticDryerPaintRobotSystem
from src.robot_systems.paint_tray_dry.paint_robot_system import TrayDryerPaintRobotSystem
import types
import unittest
from src.robot_systems.paint import paint_system_config
from src.robot_systems.paint.paint_robot_system import (PaintRobotSystem, with_paint_system_overrides)
from src.robot_systems.paint.application_wiring import _bypass_contour_preparation_enabled


class PaintSystemOverrideTests(unittest.TestCase):
    def test_empty_overrides_preserve_profile_behavior(self):
        for system in (TrayDryerPaintRobotSystem, AutomaticDryerPaintRobotSystem):
            configured = with_paint_system_overrides(system, types.SimpleNamespace())
            self.assertEqual(configured.ui_config, system.ui_config)
            self.assertEqual(configured.shell, system.shell)
            self.assertEqual(configured.metadata, system.metadata)

    def test_ui_apps_and_diagnostics_override_only_selected_system(self):
        override = types.SimpleNamespace(SHOW_DASHBOARD_CAMERA_PREVIEW=True, PAINT_ADJUSTMENT_APP=False, BYPASS_CONTOUR_PREPARATION=True)
        tray = with_paint_system_overrides(TrayDryerPaintRobotSystem, override)
        automatic = with_paint_system_overrides(AutomaticDryerPaintRobotSystem, types.SimpleNamespace())
        self.assertTrue(tray.ui_config.show_camera_preview)
        self.assertFalse(tray.ui_config.show_drying_mode_control)
        self.assertNotIn('PaintAdjustment', [spec.name for spec in tray.shell.applications])
        self.assertTrue(_bypass_contour_preparation_enabled(tray()))
        self.assertFalse(_bypass_contour_preparation_enabled(automatic()))
        self.assertFalse(paint_system_config.BYPASS_CONTOUR_PREPARATION)
        self.assertEqual(automatic.ui_config, AutomaticDryerPaintRobotSystem.ui_config)
        self.assertEqual(PaintRobotSystem.ui_config.show_camera_preview, paint_system_config.SHOW_DASHBOARD_CAMERA_PREVIEW)

    def test_unknown_override_fails(self):
        with self.assertRaisesRegex(ValueError, 'Unknown paint configuration overrides'):
            with_paint_system_overrides(TrayDryerPaintRobotSystem, types.SimpleNamespace(MISSPELLED_OPTION=True))

    def test_profile_providers_apply_their_own_module(self):
        from unittest.mock import patch
        from src.robot_systems.paint_tray_dry import bootstrap_provider, paint_system_config as tray_config
        with patch.object(tray_config, 'SHOW_DASHBOARD_CAMERA_PREVIEW', True, create=True):
            system = bootstrap_provider.create_bootstrap_provider().system_class
        self.assertTrue(system.ui_config.show_camera_preview)
        self.assertEqual(system.metadata, TrayDryerPaintRobotSystem.metadata)


if __name__ == '__main__':
    unittest.main()
