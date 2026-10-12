"""Set operator-light bit 10 in the shared compact paint holding register.

Edit COMMAND below and run directly. This diagnostic deliberately bypasses the
peripheral's enabled flag without changing the saved configuration.
"""
import json
from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))

from src.engine.hardware.communication.modbus.modbus import ModbusConfig
from src.engine.hardware.communication.transport_registry import DEFAULT_TRANSPORT_REGISTRY
from src.engine.hardware.xinje import XinjeMA8X8YR


SETTINGS_DIRECTORY = (
    REPOSITORY_ROOT / 'src/robot_systems/paint_tray_dry/storage/settings/hardware'
)
COMMAND = 'off'  # Change to 'off' to clear the light bit.
LIGHT_BIT = 9  # Zero-based: mask 1024. Other output bits are preserved.


def main():
    config = ModbusConfig.from_dict(json.loads((SETTINGS_DIRECTORY / 'modbus.json').read_text()))
    binding = json.loads((SETTINGS_DIRECTORY / 'peripherals.json').read_text())['operator_lights']
    if COMMAND not in ('on', 'off'):
        raise ValueError("COMMAND must be 'on' or 'off'")
    address = XinjeMA8X8YR.resolve_output(binding['outputs']['light_10'])
    mask = 1 << LIGHT_BIT
    if not 0 <= LIGHT_BIT <= 15:
        raise ValueError('LIGHT_BIT must be within the 16-bit holding register')
    slave_id = int(binding['slave_id'])
    slave_name = config.find_slave_name(slave_id)
    connection = config.get_connection(slave_name)
    transport = DEFAULT_TRANSPORT_REGISTRY.build_for_slave_id(config, slave_id)
    print(f'Port: {connection.port}; slave: {slave_id}; register: {address}; '
          f'command: {COMMAND}; bit: {LIGHT_BIT}; mask: {mask}', flush=True)
    if not binding.get('enabled', False):
        print('Diagnostic write ignores enabled=false; saved settings are unchanged.', flush=True)
    try:
        current = transport.read_register(address)
        value = current | mask if COMMAND == 'on' else current & (~mask & 0xFFFF)
        print(f'Register before: {current:#06x}; requested: {value:#06x}', flush=True)
        transport.write_register(address, value)
        actual = transport.read_register(address)
        print(f'Register after: {actual:#06x}', flush=True)
        if bool(actual & mask) != (COMMAND == 'on'):
            raise RuntimeError('Operator-light bit did not reach the requested state')
        print('Operator-light bit verified. Check the physical lights.')
    finally:
        transport.disconnect()


if __name__ == '__main__':
    main()
