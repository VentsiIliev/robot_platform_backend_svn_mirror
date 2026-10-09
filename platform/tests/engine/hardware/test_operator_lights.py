import unittest
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import patch

from src.engine.hardware.communication.memory_register_transport import MemoryRegisterTransport
from src.engine.hardware.operator_lights.config import OperatorLightsConfig, OperatorLightsConfigSerializer
from src.engine.hardware.operator_lights.operator_lights import OperatorLights
from src.robot_systems.paint_tray_dry.service_builders import build_operator_lights_service


class OperatorLightsTests(unittest.TestCase):
    def setUp(self):
        self.transport = MemoryRegisterTransport()
        self.lights = OperatorLights(self.transport, OperatorLightsConfig(enabled=True))

    def test_switch_and_disable(self):
        self.lights.set_active(["green"])
        self.assertEqual(self.transport.read_register(1), 1)
        self.lights.set_active(["red"])
        self.assertEqual(self.transport.read_register(1), 0)
        self.assertEqual(self.lights.get_state(), {"red": True, "green": False, "orange": False})
        self.lights.set_enabled(False)
        self.lights.set_active(["orange"])
        self.assertFalse(any(self.lights.get_state().values()))
        self.assertEqual(self.transport.read_register(0), 0)

    def test_invalid_channel_does_not_change_outputs(self):
        self.lights.set_active(["green"])
        with self.assertRaises(ValueError):
            self.lights.set_active(["unknown"])
        self.assertTrue(self.lights.get_state()["green"])

    def test_snapshot_is_detached_and_close_turns_off(self):
        self.lights.set_active(["green"])
        self.lights.get_state()["green"] = False
        self.assertTrue(self.lights.get_state()["green"])
        self.lights.close()
        self.lights.close()
        self.assertEqual(self.transport.read_register(1), 0)
        with self.assertRaises(RuntimeError):
            self.lights.set_active(["red"])

    def test_configuration_roundtrip_and_validation(self):
        serializer = OperatorLightsConfigSerializer()
        config = replace(OperatorLightsConfig(), enabled=True)
        self.assertEqual(serializer.from_dict(serializer.to_dict(config)), config)
        with self.assertRaises(ValueError):
            serializer.from_dict({"channels": ["red", "red"]})
        with self.assertRaises(ValueError):
            serializer.from_dict({"enabled": "false"})

    def test_memory_builder_needs_no_hardware_settings(self):
        class Settings:
            def get(self, key):
                self_key = key.value
                if self_key != "operator_lights":
                    raise AssertionError("Unexpected hardware settings lookup")
                return OperatorLightsConfig(enabled=True)
        lights = build_operator_lights_service(SimpleNamespace(settings=Settings()))
        lights.set_active(["orange"])
        self.assertTrue(lights.get_state()["orange"])

    def test_hardware_builder_uses_peripheral_binding(self):
        from src.engine.hardware.peripherals import PeripheralBinding, PeripheralConfig
        settings = {
            "operator_lights": OperatorLightsConfig(enabled=True, transport="configured_slave"),
            "peripherals": PeripheralConfig({"operator_lights": PeripheralBinding(
                slave_id=10, outputs={"red": "Y2", "green": "Y3", "orange": "Y4"},
                commands={"on": 4, "off": 0},
            )}),
            "modbus_config": object(),
        }
        class Settings:
            def get(self, key):
                return settings[key.value]
        from src.engine.common_settings_ids import CommonSettingsID
        settings[CommonSettingsID.MODBUS_CONFIG.value] = settings["modbus_config"]
        with patch(
            "src.engine.hardware.communication.transport_registry.DEFAULT_TRANSPORT_REGISTRY.build_for_slave_id",
            return_value=self.transport,
        ) as build:
            lights = build_operator_lights_service(SimpleNamespace(settings=Settings()))
            build.assert_called_once_with(settings["modbus_config"], 10)
        lights.set_active(["green"])
        self.assertEqual(self.transport.read_register(131), 4)
        self.assertEqual(self.transport.read_register(130), 0)

    def test_disabled_physical_binding_does_not_build_transport(self):
        from src.engine.hardware.peripherals import PeripheralBinding, PeripheralConfig
        class Settings:
            def get(self, key):
                if key.value == "operator_lights":
                    return OperatorLightsConfig(transport="configured_slave")
                if key.value == "peripherals":
                    return PeripheralConfig({"operator_lights": PeripheralBinding(slave_id=0, enabled=False)})
                raise AssertionError("Disabled binding must not access hardware settings")
        self.assertIsNone(build_operator_lights_service(SimpleNamespace(settings=Settings())))

    def test_only_tray_system_declares_lights(self):
        from src.robot_systems.paint.paint_robot_system import PaintRobotSystem
        from src.robot_systems.paint_tray_dry.paint_robot_system import TrayDryerPaintRobotSystem
        from src.robot_systems.paint_auto_dry.paint_robot_system import AutomaticDryerPaintRobotSystem
        for system in (PaintRobotSystem, AutomaticDryerPaintRobotSystem):
            self.assertNotIn("operator_lights", [spec.name.value for spec in system.settings_specs])
            self.assertNotIn("operator_lights", [spec.name.value for spec in system.services])
        self.assertIn("operator_lights", [spec.name.value for spec in TrayDryerPaintRobotSystem.settings_specs])
        self.assertIn("operator_lights", [spec.name.value for spec in TrayDryerPaintRobotSystem.services])
