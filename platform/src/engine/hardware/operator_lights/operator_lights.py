from threading import RLock
from typing import Iterable

from src.engine.hardware.communication.i_register_transport import IRegisterTransport
from src.engine.hardware.operator_lights.config import LightChannel, OperatorLightsConfig
from src.engine.hardware.operator_lights.i_operator_lights import IOperatorLights


class OperatorLights(IOperatorLights):
    """Named outputs with serialized writes and a GUI-readable command snapshot."""

    def __init__(self, transport: IRegisterTransport, config: OperatorLightsConfig,
                 channels: dict[str, LightChannel] | None = None) -> None:
        self._transport = transport
        self._channels = (dict(channels) if channels is not None else
                          {name: LightChannel(index) for index, name in enumerate(config.channels)})
        if set(self._channels) != set(config.channels):
            raise ValueError("Output bindings must match configured light channels")
        addresses = [channel.address for channel in self._channels.values()]
        if len(set(addresses)) != len(addresses):
            raise ValueError("Light outputs must use distinct addresses")
        self._enabled = config.enabled
        self._state = {name: False for name in self._channels}
        self._lock = RLock()
        self._closed = False

    def set_active(self, channels: Iterable[str]) -> None:
        active = set(channels)
        with self._lock:
            if self._closed:
                raise RuntimeError("Operator lights are closed")
            unknown = active - self._channels.keys()
            if unknown:
                raise ValueError(f"Unknown light channels: {sorted(unknown)}")
            if not self._enabled:
                return
            self._apply(active)

    def _apply(self, active: set[str]) -> None:
        # Clear inactive channels first to avoid overlapping indications during switching.
        for desired in (False, True):
            for name, channel in self._channels.items():
                if (name in active) == desired:
                    self._transport.write_register(
                        channel.address, channel.on_value if desired else channel.off_value,
                    )
                    self._state[name] = desired

    def set_enabled(self, enabled: bool) -> None:
        with self._lock:
            if self._closed:
                raise RuntimeError("Operator lights are closed")
            if not enabled:
                self._enabled = False
                self._apply(set())
            else:
                self._apply(set())
                self._enabled = True

    def is_enabled(self) -> bool:
        with self._lock:
            return self._enabled

    def get_state(self) -> dict[str, bool]:
        with self._lock:
            return dict(self._state)

    def close(self) -> None:
        with self._lock:
            if self._closed:
                return
            try:
                if self._enabled or any(self._state.values()):
                    self._apply(set())
            finally:
                self._enabled = False
                self._closed = True
                self._transport.disconnect()
