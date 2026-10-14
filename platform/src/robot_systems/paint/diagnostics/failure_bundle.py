"""Persistent, best-effort evidence bundles for failed Paint cycles."""
from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from enum import Enum
import json
import logging
from pathlib import Path
import shutil
import traceback
from typing import Any

import cv2
import numpy as np

_logger = logging.getLogger(__name__)


def write_paint_failure_bundle(
    context,
    path_executor,
    output_root: str | Path,
    *,
    raised_exception: BaseException | None = None,
) -> Path | None:
    """Write everything needed to inspect/reproduce a failed cycle.

    Diagnostics are deliberately best-effort and never raise into production.
    """
    try:
        root = Path(output_root)
        root.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc)
        stem = (
            f"{timestamp.strftime('%Y%m%dT%H%M%S.%fZ')}_"
            f"cycle-{int(context.cycle_index):04d}_{context.diagnostic_cycle_id}"
        )
        staging = root / f".{stem}.writing"
        destination = root / stem
        staging.mkdir(parents=False, exist_ok=False)

        payload = {
            "schema_version": 1,
            "recorded_at_utc": timestamp.isoformat(),
            "cycle_id": context.diagnostic_cycle_id,
            "cycle": context.snapshot_dict(),
            "failure": _json_safe(context.operation_failure),
            "tray_failure": _json_safe(context.tray_failure),
            "raised_exception": _exception_payload(raised_exception),
            "raw_process_config": _json_safe(context.raw_process_config),
            "effective_process_config": _json_safe(context.process_config),
            "dry_run_placement": _json_safe(getattr(context, "dry_run_metadata", None)),
            "capture": _snapshot_metadata(context.snapshot),
            "workpiece": {
                "description": context.workpiece_description,
                "raw": _json_safe(context.raw_workpiece),
                "contour": _json_safe(context.contour),
            },
            "execution_plan": _json_safe(context.execution_plan),
            "pickup_plan": _json_safe(getattr(path_executor, "_last_pickup_plan", None)),
            "dropoff": {
                "effective_strategy": getattr(path_executor, "_cycle_dropoff_strategy", None),
                "pending_stage_pose": _json_safe(getattr(path_executor, "_pending_stage_pose", None)),
                "last_process_end_pose": _json_safe(getattr(path_executor, "_last_process_end_pose", None)),
                "last_prepositioned_start_group": getattr(path_executor, "_last_prepositioned_start_group", None),
            },
            "motion": {
                "commands": _json_safe(getattr(path_executor, "diagnostic_motion_commands", ())),
                "last_error": getattr(getattr(path_executor, "_motion", None), "last_motion_error", None),
                "last_safe_travel_error": getattr(path_executor, "_last_safe_travel_error", None),
                "pickup_contact_mode": getattr(path_executor, "_last_pickup_contact_mode", None),
            },
            "timing": {
                "state": _json_safe(context.state_timing_recorder),
                "paint": _json_safe(context.paint_timing_recorder),
                "session": _json_safe(context.paint_timing_session),
                "total_started_at_monotonic": context.total_started_at,
                "paint_started_at_monotonic": context.paint_started_at,
            },
        }
        (staging / "failure_bundle.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False),
            encoding="utf-8",
        )
        frame = getattr(context.snapshot, "frame", None)
        if isinstance(frame, np.ndarray) and frame.size:
            cv2.imwrite(str(staging / "capture.png"), frame)
        staging.rename(destination)
        _logger.error("Paint failure evidence stored at %s", destination)
        return destination
    except Exception:
        _logger.exception("Could not store Paint failure evidence")
        try:
            if "staging" in locals() and staging.exists():
                shutil.rmtree(staging)
        except Exception:
            _logger.debug("Could not remove incomplete failure bundle", exc_info=True)
        return None


def _exception_payload(exc: BaseException | None) -> dict[str, str] | None:
    if exc is None:
        return None
    return {
        "type": type(exc).__name__,
        "message": str(exc),
        "traceback": "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
    }


def _snapshot_metadata(snapshot) -> dict | None:
    if snapshot is None:
        return None
    return {
        "source": getattr(snapshot, "source", None),
        "timestamp_s": getattr(snapshot, "timestamp_s", None),
        "work_area_id": getattr(snapshot, "work_area_id", None),
        "robot_pose": _json_safe(getattr(snapshot, "robot_pose", None)),
        "contours": _json_safe(getattr(snapshot, "contours", None)),
        "frame_shape": _json_safe(getattr(getattr(snapshot, "frame", None), "shape", None)),
    }


def _json_safe(value: Any, _seen: set[int] | None = None) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    seen = set() if _seen is None else _seen
    identity = id(value)
    if identity in seen:
        return f"<{type(value).__name__}: recursive reference>"
    seen.add(identity)
    try:
        if is_dataclass(value):
            return _json_safe(asdict(value), seen)
        if isinstance(value, dict):
            return {str(key): _json_safe(item, seen) for key, item in value.items()}
        if isinstance(value, (list, tuple, set)):
            return [_json_safe(item, seen) for item in value]
        attributes = getattr(value, "__dict__", None)
        if isinstance(attributes, dict):
            public = {key: item for key, item in attributes.items() if not key.startswith("_")}
            if public:
                return {"type": type(value).__name__, **_json_safe(public, seen)}
        return repr(value)
    finally:
        seen.discard(identity)
