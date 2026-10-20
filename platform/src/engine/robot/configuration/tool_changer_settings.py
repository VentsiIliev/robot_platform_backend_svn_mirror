from dataclasses import dataclass, field
from copy import deepcopy
from typing import List, Sequence

from src.engine.repositories.interfaces import ISettingsSerializer
from src.engine.robot.interfaces.tool_definition import ToolDefinition
from src.engine.robot.tool_changer import SlotConfig, ToolChangeStep
from src.shared_contracts.declarations.tooling import ToolDefinition as ToolDefinitionDeclaration
from src.shared_contracts.declarations.tooling import ToolSlotDefinition


@dataclass
class ToolChangerSettings:
    tools: List[ToolDefinition] = field(default_factory=list)
    slots: List[SlotConfig] = field(default_factory=list)
    reference_tool_id: int = 1
    # Historical import evidence only; never replayed to the backend.
    legacy_backend_geometry: dict = field(default_factory=dict)

    def get_tool_names(self) -> List[str]:
        return [t.name for t in self.tools]

    def get_tool_options(self) -> List[ToolDefinition]:
        return list(self.tools)


class ToolChangerSettingsSerializer(ISettingsSerializer):
    def __init__(
        self,
        default_tools: Sequence[ToolDefinitionDeclaration] | None = None,
        default_slots: Sequence[ToolSlotDefinition] | None = None,
    ) -> None:
        self._default_tools = list(default_tools or [])
        self._default_slots = list(default_slots or [])

    @property
    def settings_type(self) -> str:
        return "tool_changer"

    def get_default(self) -> ToolChangerSettings:
        return ToolChangerSettings(
            tools=[
                ToolDefinition(
                    id=int(tool.id),
                    name=str(tool.name),
                    reference_tool_id=getattr(tool, "reference_tool_id", None),
                    relative_transform=list(getattr(tool, "relative_transform", [0, 0, 0, 0, 0, 0])),
                    collision_profile=str(getattr(tool, "collision_profile", "")),
                )
                for tool in self._default_tools
            ],
            slots=[
                SlotConfig(id=int(slot.id), tool_id=slot.tool_id)
                for slot in self._default_slots
            ],
        )

    def to_dict(self, settings: ToolChangerSettings) -> dict:
        return {
            **({"legacy_backend_geometry": deepcopy(settings.legacy_backend_geometry)}
               if settings.legacy_backend_geometry else {}),
            "tools": [
                {
                    "id": t.id,
                    "name": t.name,
                }
                for t in settings.tools
            ],
            "slots": [
                {
                    "slot_id": s.id,
                    "tool_id": s.tool_id,
                    "label": s.label,
                    "pickup_sequence": [step.to_dict() for step in s.pickup_sequence],
                    "dropoff_sequence": [step.to_dict() for step in s.dropoff_sequence],
                }
                for s in settings.slots
            ],
        }

    def from_dict(self, data: dict) -> ToolChangerSettings:
        return self._from_raw(data)

    def _from_raw(self, data: dict) -> ToolChangerSettings:
        raw_tools = data.get("tools")
        raw_slots = data.get("slots")
        tools = [
            ToolDefinition(
                id=int(t["id"]),
                name=str(t["name"]),
            )
            for t in (raw_tools if raw_tools is not None else [tool.to_dict() for tool in self._default_tools])
        ]
        slots = [
            SlotConfig(
                id=int(s["slot_id"]),
                tool_id=int(s["tool_id"]) if s.get("tool_id") is not None else None,
                label=str(s.get("label", "")),
                pickup_sequence=[ToolChangeStep.from_dict(step) for step in s.get("pickup_sequence", [])],
                dropoff_sequence=[ToolChangeStep.from_dict(step) for step in s.get("dropoff_sequence", [])],
            )
            for s in (
                raw_slots
                if raw_slots is not None
                else [{"slot_id": slot.id, "tool_id": slot.tool_id} for slot in self._default_slots]
            )
        ]
        legacy = deepcopy(data.get("legacy_backend_geometry", {}))
        old_geometry = [
            {key: deepcopy(value) for key, value in tool.items()
             if key in {"id", "reference_tool_id", "relative_transform", "collision_profile"}}
            for tool in (raw_tools or [])
            if any(key in tool for key in ("reference_tool_id", "relative_transform", "collision_profile"))
        ]
        if old_geometry or "reference_tool_id" in data:
            legacy = {"reference_tool_id": int(data.get("reference_tool_id", 1)), "tools": old_geometry}
        return ToolChangerSettings(tools=tools, slots=slots, legacy_backend_geometry=legacy)
