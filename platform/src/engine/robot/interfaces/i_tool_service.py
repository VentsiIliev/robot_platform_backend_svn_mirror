from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from threading import Event
from typing import TYPE_CHECKING, Optional, List
from .tool_operation_result import ToolErrorCode, ToolOperationResult

if TYPE_CHECKING:
    from ..tool_changer import ToolChangeStep

from src.engine.robot.interfaces.tool_definition import ToolDefinition


class IToolService(ABC):
    """Tool commands return typed results; legacy tuple unpacking is supported."""

    @property
    def current_tool(self) -> Optional[int]:
        """Generic name for the attached tool; current_gripper remains compatible."""
        return self.current_gripper

    @property
    @abstractmethod
    def current_gripper(self) -> Optional[int]: ...

    @abstractmethod
    def pickup_gripper(self, gripper_id: int) -> ToolOperationResult: ...

    @abstractmethod
    def drop_off_gripper(self, gripper_id: int) -> ToolOperationResult: ...

    @abstractmethod
    def get_tools(self) -> List[ToolDefinition]: ...

    def pickup_tool(self, tool_id: int, *, cancelled: Event | None = None) -> ToolOperationResult:
        if cancelled is not None:
            return ToolOperationResult.failure(ToolErrorCode.UNSUPPORTED, "Cancellable tool pickup is not supported")
        return self.pickup_gripper(tool_id)

    def drop_off_tool(self, tool_id: int, *, cancelled: Event | None = None) -> ToolOperationResult:
        if cancelled is not None:
            return ToolOperationResult.failure(ToolErrorCode.UNSUPPORTED, "Cancellable tool drop-off is not supported")
        return self.drop_off_gripper(tool_id)

    def execute_sequence(self, slot_id: int, steps: Sequence[ToolChangeStep | dict[str, object]],
                         cancelled: Event | None = None) -> ToolOperationResult:
        """Run a taught editor draft without committing physical slot occupancy."""
        return ToolOperationResult.failure(ToolErrorCode.UNSUPPORTED, "Tool sequence execution is not supported")

    def confirm_attached_tool(self, tool_id: int | None) -> ToolOperationResult:
        """Acknowledge manually inspected attachment; None means an empty flange."""
        return ToolOperationResult.failure(ToolErrorCode.UNSUPPORTED, "Tool attachment confirmation is not supported")
