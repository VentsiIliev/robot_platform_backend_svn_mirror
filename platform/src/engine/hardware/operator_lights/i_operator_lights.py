from abc import ABC, abstractmethod
from typing import Iterable
from src.engine.hardware.operator_lights.channel import ChannelRef


class IOperatorLights(ABC):
    """Synchronous output API; hardware calls belong on a worker when used by Qt."""

    @abstractmethod
    def set_active(self, channels: Iterable[ChannelRef | str]) -> None:
        """Apply the complete set of active channels; empty means all off."""

    @abstractmethod
    def get_channel(self, name: str) -> ChannelRef:
        """Resolve a configured name, raising ValueError for an unknown channel."""

    @abstractmethod
    def set_enabled(self, enabled: bool) -> None:
        """Disable by turning all channels off; enabling starts with all off."""

    @abstractmethod
    def is_enabled(self) -> bool:
        """Return the runtime enable switch without I/O."""

    @abstractmethod
    def get_state(self) -> dict[str, bool]:
        """Return last successfully written channel states without I/O."""

    @abstractmethod
    def close(self) -> None:
        """Turn outputs off and release the transport."""
