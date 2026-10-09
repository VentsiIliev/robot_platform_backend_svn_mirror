from threading import RLock

from src.engine.hardware.communication.i_register_transport import IRegisterTransport


class MemoryRegisterTransport(IRegisterTransport):
    """Thread-safe test transport with no hardware I/O."""

    def __init__(self) -> None:
        self._values: dict[int, int] = {}
        self._lock = RLock()

    def read_register(self, address: int) -> int:
        with self._lock:
            return self._values.get(address, 0)

    def write_register(self, address: int, value: int) -> None:
        with self._lock:
            self._values[address] = value
