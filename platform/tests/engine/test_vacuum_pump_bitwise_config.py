import json
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from src.engine.common_settings_ids import CommonSettingsID
from src.engine.hardware.communication.modbus.modbus import ModbusConfig
from src.engine.hardware.communication.modbus.modbus_bitwise_fc16_transport import ModbusBitwiseFc16Transport
from src.engine.hardware.peripherals import PeripheralConfig
from src.engine.hardware.vacuum_pump.modbus.modbus_vacuum_pump_factory import build_modbus_vacuum_pump_controller
from src.engine.hardware.vacuum_pump.models.vacuum_pump_config import VacuumPumpConfig
from src.robot_systems.paint.service_builders import build_vacuum_pump_service
from src.robot_systems.paint.component_ids import SettingsID


class VacuumPumpBitwiseConfigTests(unittest.TestCase):
    def config(self, transport='modbus_bitwise_fc16'):
        return ModbusConfig.from_dict({'port': '/dev/test-pump', 'slaves': {
            'default': {'slave_address': 10, 'transport_type': transport, 'bitwise_register': 1}}})

    def test_legacy_masks_and_overlapping_bits_are_rejected_before_transport_creation(self):
        configs = [
            VacuumPumpConfig(pump_register=0, blow_off_register=2, blow_off_on_value=4),
            VacuumPumpConfig(pump_register=1, blow_off_register=1),
            VacuumPumpConfig(pump_register='Y2'),
            VacuumPumpConfig(pump_register=0, on_value=4),
        ]
        with patch('src.engine.hardware.communication.transport_registry.DEFAULT_TRANSPORT_REGISTRY.build_for_slave') as build:
            for config in configs:
                with self.subTest(config=config), self.assertRaises(ValueError):
                    build_modbus_vacuum_pump_controller(self.config(), config)
            build.assert_not_called()

    def test_standard_register_transport_preserves_word_value_contract(self):
        config = VacuumPumpConfig(pump_register=1, blow_off_register=1, blow_off_on_value=4)
        with patch('src.engine.hardware.communication.transport_registry.DEFAULT_TRANSPORT_REGISTRY.build_for_slave'):
            controller = build_modbus_vacuum_pump_controller(self.config('modbus_register_fc16'), config)
        self.assertEqual(controller._config.blow_off_on_value, 4)

    def test_tray_profile_pulses_bit_two_and_preserves_unrelated_outputs(self):
        root = Path(__file__).resolve().parents[2] / 'src/robot_systems/paint_tray_dry/storage/settings/hardware'
        modbus = ModbusConfig.from_dict(json.loads((root / 'modbus.json').read_text()))
        peripherals = PeripheralConfig.from_dict(json.loads((root / 'peripherals.json').read_text()))
        settings = {CommonSettingsID.MODBUS_CONFIG: modbus, SettingsID.PERIPHERALS: peripherals}
        ctx = SimpleNamespace(settings=SimpleNamespace(get=settings.__getitem__))
        # Bit 9 and the tray fan's configured bit 1 already belong to other outputs.
        original = (1 << 9) | (1 << 1)
        word = [original]
        instrument = MagicMock()
        instrument.read_register.side_effect = lambda *a, **k: word[0]
        def write(address, values):
            word[0] = values[0]
        instrument.write_registers.side_effect = write
        with patch.object(ModbusBitwiseFc16Transport, '_session') as session, patch(
            'src.engine.hardware.vacuum_pump.vacuum_pump_controller.time.sleep'):
            session.return_value.__enter__.return_value = instrument
            controller = build_vacuum_pump_service(ctx)
            self.assertIsNotNone(controller)
            self.assertTrue(controller.turn_on())
            self.assertEqual(word[0], original | 1)
            self.assertTrue(controller.turn_off())
        written = [call.args[1][0] for call in instrument.write_registers.call_args_list]
        self.assertEqual(written, [original, original | 1, original, original | 4, original])
        self.assertEqual(word[0], original)
        instrument.write_register.assert_not_called()
