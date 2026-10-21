"""Saved/effective values and independently observed application state."""
from typing import Any
from runtime_api.contracts import ErrorInfo, ResponseBody


class ConfigurationResponse(ResponseBody, total=False):
    profile: str
    active_profile: str
    section: str
    sections: list[str]
    authority: str
    schema_version: int
    revision: str
    saved: dict[str, Any]
    applied: dict[str, Any] | None
    pending_application: bool
    application_error: str | None
    application_error_info: ErrorInfo | None
    restart_required: bool | None
    tools: dict[str, Any]
    tool_registry: dict[str, list[float]]
    tool_id_map: dict[int | str, str]
    workobject_registry: dict[str, list[float]]
    workobject_id_map: dict[int | str, str]
    config: dict[str, Any]


class RegistryResponse(ResponseBody, total=False):
    """Legacy registry endpoints retain saved:boolean; new configuration routes use saved:object."""
    revision: str
    profile: str
    saved: bool
    pending_application: bool
    application_error: str | None
    tool_registry: dict[str, list[float]]
    tool_id_map: dict[int | str, str]
    tool_collision_profile_map: dict[str, str]
    tool_collision_profiles: dict[str, Any]
    workobject_registry: dict[str, list[float]]
    workobject_id_map: dict[int | str, str]
    default_workobject_id: int
