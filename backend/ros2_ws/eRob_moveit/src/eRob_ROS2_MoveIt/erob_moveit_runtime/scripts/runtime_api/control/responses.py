"""Control acknowledgements describe requested and actual hardware state separately."""
from typing import Any
from runtime_api.contracts import ResponseBody


class ControlResponse(ResponseBody, total=False):
    command_accepted: bool
    desired_enabled: bool
    actual_enabled: bool
    requested_enabled: bool
    verified: bool
    state: str
    message: str
    reason: str
    result: int
    port: int
    value: int
    enabled: bool
    suppressed: bool
    running: bool
    already_running: bool
    config: dict[str, Any]
    request: dict[str, Any]
