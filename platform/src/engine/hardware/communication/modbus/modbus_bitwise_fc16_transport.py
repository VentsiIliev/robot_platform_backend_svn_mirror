"""Logical binary outputs backed by one shared FC16 holding register."""
from .modbus_register_transport import ModbusRegisterTransport
from .serial_bus import serial_bus_session


class ModbusBitwiseFc16Transport(ModbusRegisterTransport):
    """Addresses are zero-based bits 0..15; values are 0 or 1, never words.

    Read the configured output register with FC3 and update it with FC16.
    The process-wide serial bus lock spans both exchanges, including across
    separate transport instances. Other processes/external writers must not
    modify this output image concurrently.
    """

    def __init__(self, *args, holding_register=1, **kwargs):
        if type(holding_register) is not int or not 0 <= holding_register <= 65535:
            raise ValueError('holding_register must be an integer in 0..65535')
        super().__init__(*args, **kwargs)
        self._holding_register = holding_register

    @staticmethod
    def _validate_range(address, count):
        if type(address) is not int or type(count) is not int or count < 1 or not 0 <= address < address + count <= 16:
            raise ValueError('Bit addresses must be within 0..15')

    def read_register(self, address):
        return self.read_registers(address, 1)[0]

    def read_registers(self, address, count):
        self._validate_range(address, count)
        with serial_bus_session(self._port, self._timeout):
            word = super().read_register(self._holding_register)
            return [(word >> bit) & 1 for bit in range(address, address + count)]

    def write_register(self, address, value):
        self.write_registers(address, [value])

    def write_registers(self, address, values):
        values = list(values)
        self._validate_range(address, len(values))
        if any(not isinstance(value, int) or value not in (0, 1) for value in values):
            raise ValueError('Bitwise output values must be 0 or 1')
        with serial_bus_session(self._port, self._timeout):
            word = super().read_register(self._holding_register)
            for bit, value in enumerate(values, start=address):
                mask = 1 << bit
                word = word | mask if value else word & (~mask & 0xFFFF)
            super().write_registers(self._holding_register, [word])
