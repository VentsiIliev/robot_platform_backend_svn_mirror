"""Strict JSON reads with explicit failure categories, without fallback writes."""
from dataclasses import dataclass
from enum import Enum
import json
import math
from pathlib import Path
from typing import Generic, TypeVar

T = TypeVar('T')


class StoreStatus(str, Enum):
    OK = 'ok'
    MISSING = 'missing'
    EMPTY = 'empty'
    CORRUPT = 'corrupt'
    INACCESSIBLE = 'inaccessible'


class JsonStoreError(ValueError):
    def __init__(self, path, status: StoreStatus, detail: str):
        self.path = str(path)
        self.status = status
        super().__init__(f'{self.path}: {status.value}: {detail}')


@dataclass(frozen=True)
class LoadResult(Generic[T]):
    status: StoreStatus
    value: T | None = None
    detail: str | None = None


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Duplicate JSON key: {key}')
        result[key] = value
    return result


def _invalid_constant(value):
    raise ValueError(f'Nonfinite JSON number: {value}')


def _finite_float(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f'Nonfinite JSON number: {value}')
    return result


def read_json_object(path: Path) -> dict:
    try:
        text = Path(path).read_text(encoding='utf-8')
    except FileNotFoundError as exc:
        raise JsonStoreError(path, StoreStatus.MISSING, str(exc)) from exc
    except UnicodeError as exc:
        raise JsonStoreError(path, StoreStatus.CORRUPT, str(exc)) from exc
    except OSError as exc:
        raise JsonStoreError(path, StoreStatus.INACCESSIBLE, str(exc)) from exc
    if not text.strip():
        raise JsonStoreError(path, StoreStatus.EMPTY, 'File has no JSON document')
    try:
        data = json.loads(text, object_pairs_hook=_pairs, parse_constant=_invalid_constant, parse_float=_finite_float)
        if not isinstance(data, dict):
            raise ValueError('Expected a JSON object')
        return data
    except (ValueError, TypeError) as exc:
        raise JsonStoreError(path, StoreStatus.CORRUPT, str(exc)) from exc
