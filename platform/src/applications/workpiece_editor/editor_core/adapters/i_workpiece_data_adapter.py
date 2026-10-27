from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from contour_editor.persistence.data.editor_data_model import ContourEditorData


class IWorkpieceDataAdapter(ABC):
    """Convert between system-specific workpiece payloads/objects and editor data."""

    def get_persistent_metadata(self, raw: dict) -> dict:
        """Return system-owned metadata that must survive edits to visible settings."""
        return {}

    @abstractmethod
    def from_workpiece(self, workpiece) -> ContourEditorData: ...

    @abstractmethod
    def to_workpiece_data(
        self,
        editor_data: ContourEditorData,
        default_settings: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]: ...

    @abstractmethod
    def from_raw(self, raw: dict) -> ContourEditorData: ...

    @abstractmethod
    def print_summary(self, editor_data: ContourEditorData) -> None: ...
