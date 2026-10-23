"""Configuration mutation DTOs; revisions are mandatory and profile-bound."""
from dataclasses import dataclass
from typing import Any, Literal

Section = Literal['calibration', 'sensorless_collision', 'cell_scene']


def section_name(value: str) -> Section:
    if value not in ('calibration', 'sensorless_collision', 'cell_scene'):
        raise ValueError(f'Unknown configuration section: {value}')
    return value


@dataclass(frozen=True)
class ConfigurationUpdateRequest:
    expected_revision: str
    changes: dict[str, Any]

    @classmethod
    def parse(cls, data: dict | None, *, apply_only: bool = False):
        if not isinstance(data, dict):
            raise ValueError('Request body must be a JSON object')
        allowed = {'expected_revision'} if apply_only else {'expected_revision', 'changes'}
        unknown = sorted(set(data) - allowed)
        if unknown:
            raise ValueError(f'Unsupported configuration request fields: {unknown}')
        revision = data.get('expected_revision')
        if not isinstance(revision, str) or not revision.strip():
            raise ValueError('expected_revision is required; reload the configuration before editing')
        changes = {} if apply_only else data.get('changes')
        if not isinstance(changes, dict) or not apply_only and not changes:
            raise ValueError('A non-empty changes object is required')
        return cls(revision, dict(changes))
