import unittest
from unittest.mock import MagicMock, patch
from concurrent.futures import ThreadPoolExecutor

from src.engine.hardware.communication.modbus.modbus_bitwise_fc16_transport import ModbusBitwiseFc16Transport
from src.engine.hardware.communication.modbus.modbus import ModbusConfig
from src.engine.hardware.communication.transport_registry import DEFAULT_TRANSPORT_REGISTRY


class BitwiseFc16Tests(unittest.TestCase):
    def test_set_clear_preserves_other_bits_and_uses_fc16(self):
        transport = ModbusBitwiseFc16Transport(port='/dev/test-bitwise', slave_address=10)
        instrument = MagicMock()
        instrument.read_register.side_effect = [0x0201, 0x0601]
        with patch.object(transport, '_session') as session:
            session.return_value.__enter__.return_value = instrument
            transport.write_register(10, 1)
            transport.write_register(9, 0)
        self.assertEqual(instrument.write_registers.call_args_list[0].args, (1, [0x0601]))
        self.assertEqual(instrument.write_registers.call_args_list[1].args, (1, [0x0401]))
        instrument.read_register.assert_called_with(1, functioncode=3)
        instrument.write_register.assert_not_called()

    def test_batch_reads_and_writes_logical_bits(self):
        transport = ModbusBitwiseFc16Transport(port='/dev/test-bitwise', slave_address=10)
        instrument = MagicMock()
        instrument.read_register.return_value = 0x0201
        with patch.object(transport, '_session') as session:
            session.return_value.__enter__.return_value = instrument
            self.assertEqual(transport.read_registers(9, 2), [1, 0])
            transport.write_registers(9, [0, 1])
        instrument.write_registers.assert_called_once_with(1, [0x0401])

    def test_invalid_commands_do_no_io(self):
        transport = ModbusBitwiseFc16Transport(port='/dev/test-bitwise', slave_address=10)
        with patch.object(transport, '_session') as session:
            for address, values in [(16, [1]), (-1, [0]), (15, [1, 0]), (1, [10]), (1, [])]:
                with self.assertRaises(ValueError):
                    transport.write_registers(address, values)
            session.assert_not_called()

    def test_registry_and_configuration_roundtrip(self):
        config = ModbusConfig.from_dict({'slaves': {'lights': {
            'slave_address': 10, 'transport_type': 'modbus_bitwise_fc16', 'bitwise_register': 7}}})
        config = ModbusConfig.from_dict(config.to_dict())
        transport = DEFAULT_TRANSPORT_REGISTRY.build_for_slave(config, 'lights')
        self.assertIsInstance(transport, ModbusBitwiseFc16Transport)
        self.assertEqual(transport._holding_register, 7)

    def test_instances_share_lock_for_entire_read_modify_write(self):
        import time
        word = [1]
        instrument = MagicMock()
        def read(*args, **kwargs):
            previous = word[0]
            time.sleep(0.01)
            return previous
        def write(address, values):
            word[0] = values[0]
        instrument.read_register.side_effect = read
        instrument.write_registers.side_effect = write
        transports = [ModbusBitwiseFc16Transport(port='/dev/test-shared', slave_address=10) for _ in range(2)]
        with patch.object(ModbusBitwiseFc16Transport, '_session') as session:
            session.return_value.__enter__.return_value = instrument
            with ThreadPoolExecutor(2) as workers:
                futures = [workers.submit(t.write_register, bit, 1) for t, bit in zip(transports, (9, 10))]
                for future in futures:
                    future.result()
        self.assertEqual(word[0], 0x0601)

    def test_same_slave_supports_explicit_word_transport_override(self):
        from src.engine.hardware.communication.modbus.modbus_fc16_register_transport import ModbusFc16RegisterTransport
        from src.engine.hardware.peripherals import PeripheralConfig
        config = ModbusConfig.from_dict({'port': '/dev/shared', 'slaves': {'default': {
            'slave_address': 10, 'transport_type': 'modbus_bitwise_fc16'}}})
        peripherals = PeripheralConfig.from_dict({'paint_head': {
            'slave_id': 10, 'transport_type': 'modbus_register_fc16'}})
        binding = PeripheralConfig.from_dict(peripherals.to_dict()).get('paint_head')
        bits = DEFAULT_TRANSPORT_REGISTRY.build_for_slave(config, 'default')
        words = DEFAULT_TRANSPORT_REGISTRY.build_for_slave(config, 'default',
                                                          transport_type=binding.transport_type)
        self.assertIsInstance(bits, ModbusBitwiseFc16Transport)
        self.assertIsInstance(words, ModbusFc16RegisterTransport)
        self.assertEqual((bits._port, bits._slave_address), (words._port, words._slave_address))
        self.assertEqual(config.get_slave('default').transport_type, 'modbus_bitwise_fc16')
