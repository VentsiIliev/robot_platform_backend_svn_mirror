"""Startup policy for the optional machine-history capability."""
from dataclasses import dataclass
import os


@dataclass(frozen=True)
class DiagnosticsConfig:
    enabled: bool = True
    capture_logs: bool = True
    console_events: bool = False

    @classmethod
    def from_mapping(cls, payload=None, *, environ=None):
        if payload is None:
            payload = {}
        if not isinstance(payload, dict):
            raise RuntimeError("'diagnostics' must be a JSON object")
        values = {}
        defaults = cls()
        for name in ('enabled', 'capture_logs', 'console_events'):
            value = payload.get(name, getattr(defaults, name))
            if type(value) is not bool:
                raise RuntimeError(f"'diagnostics.{name}' must be a boolean")
            values[name] = value
        override = (os.environ if environ is None else environ).get('ROBOT_PLATFORM_DIAGNOSTICS_ENABLED')
        if override is not None:
            if override not in ('0', '1'):
                raise RuntimeError('ROBOT_PLATFORM_DIAGNOSTICS_ENABLED must be 0 or 1')
            values['enabled'] = override == '1'
        return cls(**values)
