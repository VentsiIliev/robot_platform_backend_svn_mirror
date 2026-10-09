from dataclasses import dataclass, field

from src.engine.repositories.interfaces.settings_serializer import ISettingsSerializer


@dataclass(frozen=True)
class LightChannel:
    address: int
    on_value: int = 1
    off_value: int = 0

    def __post_init__(self) -> None:
        if self.address < 0 or self.on_value == self.off_value:
            raise ValueError("Light channels need a nonnegative address and distinct on/off values")


@dataclass(frozen=True)
class OperatorLightsConfig:
    enabled: bool = False
    transport: str = "memory"
    channels: tuple[str, ...] = ("red", "green", "orange")
    state_mapping: dict[str, tuple[str, ...]] = field(default_factory=lambda: {
        "idle": (), "running": ("green",), "paused": ("orange",),
        "stopped": (), "error": ("red",),
    })

    def __post_init__(self) -> None:
        if self.transport not in ("memory", "configured_slave"):
            raise ValueError(f"Unknown operator lights transport: {self.transport}")
        if not self.channels or any(not name.strip() for name in self.channels):
            raise ValueError("Light channels require nonempty names")
        if len(set(self.channels)) != len(self.channels):
            raise ValueError("Light channel names must be distinct")
        for names in self.state_mapping.values():
            if isinstance(names, str) or any(name not in self.channels for name in names):
                raise ValueError("State mappings must contain configured channel names")


class OperatorLightsConfigSerializer(ISettingsSerializer[OperatorLightsConfig]):
    @property
    def settings_type(self) -> str:
        return "operator_lights"

    def get_default(self) -> OperatorLightsConfig:
        return OperatorLightsConfig()

    def to_dict(self, settings: OperatorLightsConfig) -> dict:
        return {
            "enabled": settings.enabled,
            "transport": settings.transport,
            "channels": list(settings.channels),
            "state_mapping": {state: list(names) for state, names in settings.state_mapping.items()},
        }

    def from_dict(self, data: dict) -> OperatorLightsConfig:
        defaults = self.to_dict(self.get_default())
        values = {**defaults, **data}
        if not isinstance(values["enabled"], bool):
            raise ValueError("Operator lights enabled must be a boolean")
        if not isinstance(values["channels"], list) or any(
            not isinstance(name, str) for name in values["channels"]
        ):
            raise ValueError("Operator light channels must be a list of names")
        mapping = values["state_mapping"]
        if not isinstance(mapping, dict) or any(
            not isinstance(state, str) or not isinstance(names, list)
            or any(not isinstance(name, str) for name in names)
            for state, names in mapping.items()
        ):
            raise ValueError("State mapping must map state names to lists of channel names")
        return OperatorLightsConfig(
            enabled=values["enabled"], transport=values["transport"],
            channels=tuple(values["channels"]),
            state_mapping={state: tuple(names) for state, names in mapping.items()},
        )
