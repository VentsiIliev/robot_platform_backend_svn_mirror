"""Read-only runtime snapshots, including partial availability and startup progress."""
from typing import Any
from runtime_api.contracts import ResponseBody


class StateResponse(ResponseBody, total=False):
    position: list[float]
    velocity: list[float]
    status: str | dict[str, Any]
    runtime_ready: bool
    motion_stack_ready: bool
    runtime_initialized: bool
    unavailable_fields: list[str]
    supported: bool
    active: bool
    phase: str
    message: str
    ready: bool
    conditional_servo: dict[str, Any]
    plan_id: str
    state: str
