"""Read slave 10, or explicitly write a value with FC16 and read it back.

Set WRITE_VALUE to 1 to test a write, or None to read only.
"""

import logging
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.engine.hardware.communication.modbus.modbus_fc16_register_transport import (
    ModbusFc16RegisterTransport,
)

ADDRESS = 2
WRITE_VALUE = 200  # Set to 1 to write 1 and verify the readback.


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)-8s] %(name)s — %(message)s",
)

def write_and_read_back(
    transport: ModbusFc16RegisterTransport, address: int, value: int
) -> int:
    transport.write_register(address, value)
    print(f"Slave 10, address {address}: wrote {value} using FC16")
    actual = transport.read_register(address)
    print(f"Slave 10, address {address}: read back {actual} (0x{actual:04X})")
    if actual != value:
        raise RuntimeError(f"Readback mismatch: wrote {value}, read {actual}")
    return actual


def main() -> None:
    transport = ModbusFc16RegisterTransport(
        port="/dev/ttyUSB0",
        slave_address=10,
        baudrate=57600,
        bytesize=8,
        stopbits=1,
        parity="N",
        timeout=0.5,
    )
    try:
        if WRITE_VALUE is None:
            value = transport.read_register(ADDRESS)
            print(f"Slave 10, address {ADDRESS}: {value} (0x{value:04X})")
        else:
            write_and_read_back(transport, ADDRESS, WRITE_VALUE)
    finally:
        transport.disconnect()


if __name__ == "__main__":
    main()
