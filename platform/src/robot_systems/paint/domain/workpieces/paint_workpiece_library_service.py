import logging
from uuid import uuid4
from typing import List, Optional
from src.applications.workpiece_library.service.i_workpiece_duplicator import IWorkpieceDuplicator

from src.applications.workpiece_library.domain.workpiece_schema import (
    WorkpieceFieldDescriptor,
    WorkpieceRecord,
    WorkpieceSchema,
)

_logger = logging.getLogger(__name__)


def build_paint_workpiece_library_schema() -> WorkpieceSchema:
    return WorkpieceSchema(
        id_key="id",
        name_key="name",
        fields=[
            WorkpieceFieldDescriptor(key="workpieceId", label="ID", table_display=True, detail_display=True, editable=False),
            WorkpieceFieldDescriptor(key="name", label="Name", table_display=True, detail_display=True, editable=True, widget="text"),
            WorkpieceFieldDescriptor(key="date", label="Date", table_display=True, detail_display=True, editable=False),
            WorkpieceFieldDescriptor(key="description", label="Description", table_display=False, detail_display=True, editable=True, widget="text"),
            WorkpieceFieldDescriptor(key="height_mm", label="Height (mm)", table_display=True, detail_display=True, editable=True, widget="text"),
        ],
    )


class PaintWorkpieceLibraryService(IWorkpieceDuplicator):
    def __init__(self, workpiece_service):
        self._service = workpiece_service

    def get_schema(self) -> WorkpieceSchema:
        return build_paint_workpiece_library_schema()

    def list_all(self) -> List[WorkpieceRecord]:
        records: List[WorkpieceRecord] = []
        for meta in self._service.list_all():
            raw = (
                {}
                if "workpieceId" in meta
                else self.load_raw(str(meta.get("id", ""))) or {}
            )
            records.append(
                WorkpieceRecord(
                    {
                        "id": meta.get("id", ""),
                        "workpieceId": meta.get("workpieceId", raw.get("workpieceId", "")),
                        "name": raw.get("name", meta.get("name", "")),
                        "date": meta.get("date", ""),
                        "description": meta.get("description", raw.get("description", "")),
                        "height_mm": meta.get("height_mm", raw.get("height_mm", "")),
                        "dimensions": meta.get("dimensions", ""),
                    }
                )
            )
        return records

    def update(self, storage_id: str, updates: dict) -> tuple[bool, str]:
        raw = self.load_raw(storage_id)
        if raw is None:
            return False, f"Workpiece '{storage_id}' not found"
        updates = dict(updates or {})
        updates.pop("workpieceId", None)
        if "height_mm" in updates:
            try:
                updates["height_mm"] = float(updates["height_mm"])
            except (TypeError, ValueError):
                return False, "Height (mm) must be a number"
        raw.update(updates)
        return self._service.update(storage_id, raw)

    def delete(self, workpiece_id: str) -> tuple[bool, str]:
        return self._service.delete(workpiece_id)

    def duplicate(self, storage_id: str) -> tuple[bool, str]:
        """Save an independent copy with a new business ID and storage location."""
        raw = self.load_raw(storage_id)
        if raw is None:
            return False, f"Workpiece '{storage_id}' not found"
        raw = dict(raw)
        raw["workpieceId"] = uuid4().hex
        raw["name"] = f"{raw.get('name', '')} (copy)"
        ok, message = self._service.save(raw)
        return (True, "Workpiece duplicated") if ok else (False, message)

    def get_thumbnail(self, workpiece_id: str) -> Optional[bytes]:
        return self._service.get_thumbnail_bytes(workpiece_id)

    def load_raw(self, storage_id: str) -> Optional[dict]:
        return self._service.load_raw(storage_id)
