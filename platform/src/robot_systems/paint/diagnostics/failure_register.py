"""Append-only register of Paint failures, separate from detailed evidence bundles."""
from __future__ import annotations

import json
import logging
from pathlib import Path
import threading

_write_lock = threading.Lock()
_logger = logging.getLogger(__name__)


def summarize_failure_workpiece(description: str, raw_workpiece, dry_run_metadata) -> dict | None:
    """Identify the current part without copying large contour arrays into the register."""
    raw = raw_workpiece if isinstance(raw_workpiece, dict) else {}
    placements = {}
    for key, metadata in (dry_run_metadata or {}).items():
        if not isinstance(metadata, dict):
            continue
        item = metadata.get("workpiece") or {}
        placements[key] = {
            "id": item.get("id"),
            "shape_type": item.get("shape_type"),
            "width_mm": item.get("width_mm"),
            "height_mm": item.get("height_mm"),
            **{
                field: metadata.get(field)
                for field in (
                    "dataset_manifest", "dataset_index", "original_size_mm", "fit_scale",
                    "angle_deg", "center_mm", "work_area_id", "placement_mode",
                )
            },
        }
    if not description and not raw and not placements:
        return None
    selected = placements.get("paint") or placements.get("magazine") or {}
    return {
        "id": selected.get("id") or raw.get("workpieceId"),
        "name": raw.get("name"),
        "description": description or None,
        "prepared_workpiece_id": raw.get("workpieceId"),
        "dry_run_placements": placements or None,
    }


def append_paint_failure_record(output_root: str | Path, record: dict) -> None:
    """Append one JSON record; diagnostic storage errors must not affect robot stopping."""
    try:
        path = Path(output_root) / "failure_register.jsonl"
        line = json.dumps(record, ensure_ascii=False, default=str) + "\n"
        with _write_lock:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as stream:
                stream.write(line)
    except Exception:
        _logger.exception("Could not append Paint failure register")
