"""Outcomes for optional trajectory diagnostics, independent of motion success."""
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import TypeAlias


class ExportFailureCode(StrEnum):
    INVALID_INPUT = "invalid_input"
    FILESYSTEM = "filesystem"
    UNAVAILABLE = "unavailable"
    INTERNAL = "internal"


@dataclass(frozen=True)
class ExportWritten:
    stage: str
    artifacts: tuple[Path, ...]


@dataclass(frozen=True)
class ExportSkipped:
    stage: str
    reason: str


@dataclass(frozen=True)
class ExportFailed:
    code: ExportFailureCode
    stage: str
    phase: str
    message: str
    completed_artifacts: tuple[Path, ...] = ()


ExportResult: TypeAlias = ExportWritten | ExportSkipped | ExportFailed
