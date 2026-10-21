"""Shared immutable API settings and transport-neutral result helpers."""
from dataclasses import dataclass, field
from runtime_api.contracts import to_jsonable
from runtime_api.motion.requests import MotionDefaults


@dataclass(frozen=True)
class ApiSettings:
    port: int = 5000
    execution_ws_port: int = 5002
    drive_verify_timeout_s: float = 5.0
    motion_defaults: MotionDefaults = field(default_factory=MotionDefaults)


def http_status_for_state(state: str | None, default: int = 500) -> int:
    return {'HARDWARE_NOT_READY': 503, 'UNSUPPORTED': 501}.get(state, default)


def as_dict(value, error_message: str) -> dict:
    value = to_jsonable(value)
    return value if isinstance(value, dict) else {'success': False, 'error': error_message}
