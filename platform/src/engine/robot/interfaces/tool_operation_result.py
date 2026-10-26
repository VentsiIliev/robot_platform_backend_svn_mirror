"""Typed outcomes shared by tool services and their callers."""
from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from enum import Enum
from typing import Literal, overload


class ToolErrorCode(str, Enum):
    BUSY = "BUSY"
    RECOVERY_REQUIRED = "RECOVERY_REQUIRED"
    TOOL_NOT_FOUND = "TOOL_NOT_FOUND"
    SLOT_NOT_FOUND = "SLOT_NOT_FOUND"
    TOOL_ALREADY_HELD = "TOOL_ALREADY_HELD"
    TOOL_NOT_HELD = "TOOL_NOT_HELD"
    SLOT_ASSIGNMENT_CHANGED = "SLOT_ASSIGNMENT_CHANGED"
    SLOT_OCCUPIED = "SLOT_OCCUPIED"
    SEQUENCE_NOT_CONFIGURED = "SEQUENCE_NOT_CONFIGURED"
    INVALID_SEQUENCE = "INVALID_SEQUENCE"
    CONFIRMATION_REQUIRED = "CONFIRMATION_REQUIRED"
    CONFIRMATION_DECLINED = "CONFIRMATION_DECLINED"
    CONFIRMATION_FAILED = "CONFIRMATION_FAILED"
    ACTIVATION_UNAVAILABLE = "ACTIVATION_UNAVAILABLE"
    ACTIVATION_FAILED = "ACTIVATION_FAILED"
    ROBOT_UNAVAILABLE = "ROBOT_UNAVAILABLE"
    ROBOT_NOT_READY = "ROBOT_NOT_READY"
    POSITION_NOT_CONFIGURED = "POSITION_NOT_CONFIGURED"
    POSE_UNAVAILABLE = "POSE_UNAVAILABLE"
    NOT_AT_TOOL_CHANGER = "NOT_AT_TOOL_CHANGER"
    CANCELLED = "CANCELLED"
    MOTION_FAILED = "MOTION_FAILED"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    UNSUPPORTED = "UNSUPPORTED"
    UNEXPECTED_ERROR = "UNEXPECTED_ERROR"


@dataclass(frozen=True)
class ToolErrorInfo:
    code: ToolErrorCode
    message: str
    step_number: int | None = None  # One-based; None for failures before execution.
    detail: str | None = None


class ToolOperationFailure(Exception):
    """Internal validation/execution exception carrying an already classified error."""

    def __init__(self, code: ToolErrorCode, message: str, *,
                 step_number: int | None = None, detail: str | None = None) -> None:
        super().__init__(message)
        self.error = ToolErrorInfo(code, message, step_number, detail)


@dataclass(frozen=True)
class ToolOperationResult:
    message: str | None = None
    error: ToolErrorInfo | None = None

    def __post_init__(self) -> None:
        if self.error is not None:
            object.__setattr__(self, "message", self.error.message)

    @property
    def success(self) -> bool:
        return self.error is None

    @classmethod
    def failure(cls, code: ToolErrorCode, message: str, *,
                step_number: int | None = None, detail: str | None = None) -> ToolOperationResult:
        return cls(error=ToolErrorInfo(code, message, step_number, detail))

    def __bool__(self) -> bool:
        return self.success

    def as_tuple(self) -> tuple[bool, str | None]:
        """Compatibility boundary for existing (ok, message) callers."""
        return self.success, self.message

    def __iter__(self) -> Iterator[bool | str | None]:
        return iter(self.as_tuple())

    @overload
    def __getitem__(self, index: Literal[0, -2]) -> bool: ...

    @overload
    def __getitem__(self, index: Literal[1, -1]) -> str | None: ...

    @overload
    def __getitem__(self, index: int) -> bool | str | None: ...

    def __getitem__(self, index: int) -> bool | str | None:
        return self.as_tuple()[index]
