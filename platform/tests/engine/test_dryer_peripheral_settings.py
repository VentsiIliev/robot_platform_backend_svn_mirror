import unittest
from unittest.mock import MagicMock

from src.applications.device_control.dryer.application_service import (
    DryerControlService,
)
from src.engine.hardware.dryer.models.dryer_config import DryerConfig
from src.engine.hardware.peripherals import PeripheralConfigSerializer


class TestDeviceControlDryerPersistence(unittest.TestCase):
    def test_sensor_binding_zero_and_labels_preserve_input_precedence(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        from src.engine.hardware.peripherals.peripherals import PeripheralBinding, PeripheralConfig
        from src.engine.hardware.communication.modbus.modbus import ModbusConfig
        from src.robot_systems.paint.service_builders import build_vacuum_sensor_service
        from src.engine.common_settings_ids import CommonSettingsID
        from src.engine.hardware.vacuum_sensor import mock_runner

        modbus = object.__new__(ModbusConfig)
        modbus.find_slave_name = MagicMock(return_value='sensor')
        modbus.get_connection = MagicMock(return_value=MagicMock())
        modbus.get_slave = MagicMock(return_value=MagicMock())
        for inputs, outputs, expected in [({'sensor': 0}, {'sensor': 7}, 0),
                                          ({'sensor': '0'}, {'sensor': 7}, '0'),
                                          ({'sensor': 'X4'}, {'sensor': 7}, 'X4'),
                                          ({}, {'sensor': 0}, 0)]:
            with self.subTest(inputs=inputs, outputs=outputs):
                binding = PeripheralBinding(slave_id=1, inputs=inputs, outputs=outputs)
                config = PeripheralConfig(peripherals={'vacuum_sensor': binding})
                settings = MagicMock()
                settings.get.side_effect = lambda key: modbus if key == CommonSettingsID.MODBUS_CONFIG else config
                with patch('src.engine.hardware.communication.transport_registry.DEFAULT_TRANSPORT_REGISTRY.build_for_slave'), patch('src.engine.hardware.vacuum_sensor.vacuum_sensor_service.VacuumSensorService') as sensor:
                    build_vacuum_sensor_service(SimpleNamespace(settings=settings))
                    self.assertEqual(sensor.call_args.kwargs['config'].sensor_register, expected)
                with patch.object(mock_runner, '_load_modbus_config', return_value=modbus), patch.object(mock_runner, '_load_peripherals', return_value=config), patch.object(mock_runner, '_build_transport', return_value=('sensor', MagicMock())), patch.object(mock_runner, 'VacuumSensorService') as sensor, patch('builtins.print'):
                    result = mock_runner._build_sensor()
                    self.assertEqual(result[2], expected)
                    self.assertEqual(sensor.call_args.kwargs['config'].sensor_register, expected)
        restored = PeripheralBinding.from_dict({'slave_id': 1, 'inputs': {'sensor': 0}})
        self.assertEqual(restored.inputs['sensor'], '0')

    def test_absent_sensor_does_not_construct_transport(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        from src.engine.hardware.peripherals.peripherals import PeripheralBinding, PeripheralConfig
        from src.engine.hardware.communication.modbus.modbus import ModbusConfig
        from src.robot_systems.paint.service_builders import build_vacuum_sensor_service
        config = PeripheralConfig(peripherals={'vacuum_sensor': PeripheralBinding(slave_id=1)})
        settings = MagicMock()
        settings.get.side_effect = [object.__new__(ModbusConfig), config]
        with patch('src.engine.hardware.communication.transport_registry.DEFAULT_TRANSPORT_REGISTRY.build_for_slave') as transport:
            self.assertIsNone(build_vacuum_sensor_service(SimpleNamespace(settings=settings)))
            transport.assert_not_called()

    def test_dryer_status_masks_survive_settings_round_trip(self) -> None:
        serializer = PeripheralConfigSerializer()
        config = serializer.from_dict({
            "dryer": {
                "slave_id": 10,
                "statuses": {"ready": 1, "next_pos_done": 64},
            },
        })

        self.assertEqual(
            config.peripherals["dryer"].statuses,
            {"ready": 1, "next_pos_done": 64},
        )
        self.assertEqual(
            serializer.to_dict(config)["dryer"]["statuses"],
            {"ready": 1, "next_pos_done": 64},
        )

    def test_device_control_loads_and_saves_dedicated_dryer_config(self) -> None:
        settings = MagicMock()
        live_controller = MagicMock()
        current = DryerConfig(pwm_open_vrytka=700, acceleration=0.2)
        settings.get.return_value = current
        service = DryerControlService(
            settings_service=settings,
            dryer_config_key="dryer",
            live_controller=live_controller,
        )

        self.assertIs(service.load_config(), current)

        updated = DryerConfig(pwm_open_vrytka=800)
        service.save_config(updated)
        settings.save.assert_called_once_with("dryer", updated)
        live_controller.update_config.assert_called_once_with(updated)

if __name__ == "__main__":
    unittest.main()
