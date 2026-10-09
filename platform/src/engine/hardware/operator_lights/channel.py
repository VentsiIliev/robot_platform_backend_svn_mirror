from dataclasses import dataclass


@dataclass(frozen=True)
class ChannelRef:
    """Logical channel name resolved from a light service's configuration."""

    name: str
