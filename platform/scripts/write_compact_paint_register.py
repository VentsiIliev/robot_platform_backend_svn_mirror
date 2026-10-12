"""Move by a specified angle using the compact paint Modbus config."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))

from src.engine.hardware.communication.modbus.modbus import ModbusConfig
from src.engine.hardware.communication.transport_registry import (
    DEFAULT_TRANSPORT_REGISTRY,
)


REGISTER_ADDRESS = 1



# Device calibration: 0 degrees = 47, 90 degrees = 141.

MODBUS_CONFIG_PATH = (
    REPOSITORY_ROOT / "src" / "robot_systems" / "paint_tray_dry" / "storage" / "settings" / "hardware" / "modbus.json")

def main() -> int:
    with MODBUS_CONFIG_PATH.open("r", encoding="utf-8") as config_file:
        config = ModbusConfig.from_dict(json.load(config_file))

    slave_name = "default"
    connection = config.get_connection(slave_name)
    transport = DEFAULT_TRANSPORT_REGISTRY.build_for_slave(config, slave_name)

    value_to_write= 0
    transport.write_register(REGISTER_ADDRESS, value_to_write)

    value_read_back = transport.read_register(REGISTER_ADDRESS)
    print(f"Read back holding register {REGISTER_ADDRESS}: {value_read_back}")
    if value_read_back != value_to_write:
        raise RuntimeError(
            f"Readback mismatch: wrote {value_to_write}, read {value_read_back}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
