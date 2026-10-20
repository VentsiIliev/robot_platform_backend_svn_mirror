from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol


class ToolRegistryClient(Protocol):
    def get_tool_registry(self) -> dict | None: ...


class ToolActivator(Protocol):
    def set_active_tool(self, tool: int) -> bool: ...


class ToolActivationService:
    """Select an existing backend definition without changing calibrated geometry."""

    def __init__(self, registry: ToolRegistryClient, activator: ToolActivator):
        self._registry = registry
        self._activator = activator

    def activate(self, *, tool_id: int, name: str = "", reference_transform: Sequence[float] = (),
                 relative_transform: Sequence[float] = (), persist_registry: bool = True,
                 collision_profile: str = "") -> tuple[bool, str, list[float]]:
        # Legacy geometry arguments are deliberately ignored; edits are a separate operation.
        snapshot = self._registry.get_tool_registry()
        if not snapshot:
            return False, "Backend tool configuration is unavailable", []
        if snapshot.get("pending_application"):
            return False, "Saved tool configuration is pending application; restart the backend", []
        ids = snapshot.get("tool_id_map", {})
        key = ids.get(tool_id, ids.get(str(tool_id)))
        resolved = snapshot.get("tool_registry", {}).get(key)
        if resolved is None:
            return False, f"Tool {tool_id} has no backend definition. Save its geometry first.", []
        if not self._activator.set_active_tool(int(tool_id)):
            return False, f"Tool {tool_id} could not be activated", list(resolved)
        return True, f"Tool {tool_id} activated", list(resolved)
