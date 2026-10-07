import json
import logging
import os
import shutil
import tempfile
from threading import RLock
from datetime import datetime
from typing import List, Optional

import numpy as np

from src.applications.workpiece_library.workpiece_thumbnail import (
    generate_thumbnail_bytes,
)

_logger = logging.getLogger(__name__)


def _numpy_to_python(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {key: _numpy_to_python(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [_numpy_to_python(item) for item in obj]
    return obj


class WorkpieceWriteError(RuntimeError):
    """A workpiece and its required thumbnail could not be published safely."""


class JsonPaintWorkpieceRepository:
    def __init__(self, storage_root: str):
        self._lock = RLock()
        self._root = os.path.realpath(storage_root)
        os.makedirs(self._root, exist_ok=True)
        _logger.info("JsonPaintWorkpieceRepository: root -> %s", self._root)

    @staticmethod
    def _validate_storage_id(storage_id: str) -> None:
        if (not isinstance(storage_id, str) or not storage_id
                or storage_id in {".", ".."}
                or any(character in storage_id for character in ("/", "\\", "\x00"))
                or os.path.isabs(storage_id)):
            raise ValueError("Paint workpiece storage ID must be a single nonempty folder name, not a path")

    def _assert_safe_path(self, path: str) -> None:
        """Reject escapes and symlinks within the configured storage tree."""
        resolved = os.path.realpath(path)
        if os.path.commonpath((self._root, resolved)) != self._root or resolved == self._root:
            raise ValueError("Paint workpiece path escapes its storage root")
        current = self._root
        for component in os.path.relpath(path, self._root).split(os.sep):
            current = os.path.join(current, component)
            if os.path.islink(current):
                raise ValueError("Paint workpiece paths must not contain symlinks")

    def save(self, workpiece: dict) -> str:
        with self._lock:
            file_path = self._build_path()
            folder = os.path.dirname(file_path)
            storage_id = os.path.basename(folder)
            staging = tempfile.mkdtemp(prefix=".paint-save-", dir=os.path.dirname(folder))
            try:
                self._prepare_record(staging, storage_id, workpiece)
                # The record becomes visible only when both files are ready.
                os.rename(staging, folder)
                return file_path
            except Exception as exc:
                raise WorkpieceWriteError(f"Could not save paint workpiece '{storage_id}': {exc}") from exc
            finally:
                self._discard_staging(staging)

    @staticmethod
    def _prepare_record(folder: str, storage_id: str, data: dict) -> None:
        serialized = _numpy_to_python(data)
        try:
            payload = json.dumps(serialized, indent=2).encode("utf-8")
        except Exception as exc:
            raise WorkpieceWriteError(f"JSON serialization failed: {exc}") from exc
        try:
            thumbnail = generate_thumbnail_bytes(serialized)
            if not isinstance(thumbnail, bytes) or not thumbnail:
                raise ValueError("thumbnail generator returned no image")
        except Exception as exc:
            raise WorkpieceWriteError(f"Thumbnail generation failed: {exc}") from exc
        for name, content in [(f"{storage_id}_workpiece.json", payload),
                              (f"{storage_id}_thumbnail.png", thumbnail)]:
            with open(os.path.join(folder, name), "wb") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())

    @staticmethod
    def _discard_staging(folder: str) -> None:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
            except OSError:
                _logger.exception("Could not remove paint workpiece staging directory %s", folder)

    def list_all(self) -> List[dict]:
        with self._lock:
            records: List[dict] = []
            for date_dir in sorted(os.listdir(self._root)):
                date_path = os.path.join(self._root, date_dir)
                if not os.path.isdir(date_path):
                    continue
                for storage_id in sorted(os.listdir(date_path)):
                    storage_path = os.path.join(date_path, storage_id)
                    if not os.path.isdir(storage_path) or os.path.exists(os.path.join(storage_path, ".incomplete")):
                        continue
                    json_path = os.path.join(storage_path, f"{storage_id}_workpiece.json")
                    try:
                        self._validate_storage_id(storage_id)
                        self._assert_safe_path(json_path)
                        self._assert_safe_path(os.path.join(storage_path, f"{storage_id}_thumbnail.png"))
                    except ValueError as exc:
                        _logger.warning("Skipping unsafe paint workpiece %s: %s", storage_id, exc)
                        continue
                    if not os.path.exists(json_path):
                        continue
                    try:
                        with open(json_path, "r", encoding="utf-8") as handle:
                            raw = json.load(handle)
                        thumb_path = os.path.join(storage_path, f"{storage_id}_thumbnail.png")
                        records.append(
                            {
                                "id": storage_id,
                                "name": raw.get("name", ""),
                                "workpieceId": raw.get("workpieceId", ""),
                                "description": raw.get("description", ""),
                                "height_mm": raw.get("height_mm", ""),
                                "date": date_dir,
                                "path": json_path,
                                "thumbnail_path": thumb_path if os.path.exists(thumb_path) else None,
                            }
                        )
                    except Exception as exc:
                        _logger.warning("Could not read paint workpiece %s: %s", json_path, exc)
            return records

    def delete(self, storage_id: str) -> bool:
        with self._lock:
            path = self._find_file(storage_id)
            if path is None:
                return False
            try:
                shutil.rmtree(os.path.dirname(path))
                return True
            except Exception as exc:
                _logger.error("Failed to delete paint workpiece %s: %s", storage_id, exc)
                return False

    def get_thumbnail_bytes(self, storage_id: str) -> Optional[bytes]:
        with self._lock:
            path = self._find_file(storage_id)
            if path is None:
                return None
            folder = os.path.dirname(path)
            thumb_path = os.path.join(folder, f"{storage_id}_thumbnail.png")
            self._assert_safe_path(thumb_path)
            if os.path.exists(thumb_path):
                with open(thumb_path, "rb") as handle:
                    return handle.read()
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    raw = json.load(handle)
                thumb_bytes = generate_thumbnail_bytes(raw)
                if thumb_bytes:
                    with open(thumb_path, "wb") as handle:
                        handle.write(thumb_bytes)
                return thumb_bytes
            except Exception:
                _logger.exception("Failed to generate thumbnail for %s", storage_id)
                return None

    def workpiece_id_exists(self, workpiece_id: str) -> bool:
        with self._lock:
            for meta in self.list_all():
                path = meta.get("path")
                if not path:
                    continue
                try:
                    with open(path, "r", encoding="utf-8") as handle:
                        raw = json.load(handle)
                    if str(raw.get("workpieceId", "")).strip() == str(workpiece_id).strip():
                        return True
                except Exception:
                    _logger.debug("Failed while checking workpieceId existence", exc_info=True)
            return False

    def update(self, storage_id: str, data: dict) -> str:
        with self._lock:
            path = self._find_file(storage_id)
            if path is None:
                raise FileNotFoundError(f"Paint workpiece '{storage_id}' not found")
            folder = os.path.dirname(path)
            record_id = os.path.basename(folder)
            thumbnail_path = os.path.join(folder, f"{record_id}_thumbnail.png")
            self._assert_safe_path(thumbnail_path)
            staging = tempfile.mkdtemp(prefix=".paint-update-", dir=folder)
            marker_created = False
            thumbnail_published = False
            preserve_staging = False
            backup = os.path.join(staging, "previous_thumbnail.png")
            marker = os.path.join(folder, ".incomplete")
            had_thumbnail = os.path.exists(thumbnail_path)
            try:
                self._prepare_record(staging, record_id, data)
                if had_thumbnail:
                    shutil.copyfile(thumbnail_path, backup)
                # Mark unfinished publication so subsequent readers cannot use a partial pair.
                with open(marker, "x", encoding="utf-8") as handle:
                    handle.write(staging)
                marker_created = True
                os.replace(os.path.join(staging, f"{record_id}_thumbnail.png"), thumbnail_path)
                thumbnail_published = True
                os.replace(os.path.join(staging, f"{record_id}_workpiece.json"), path)
            except Exception as exc:
                if thumbnail_published:
                    try:
                        if had_thumbnail:
                            os.replace(backup, thumbnail_path)
                        else:
                            os.unlink(thumbnail_path)
                    except OSError as rollback_exc:
                        preserve_staging = True
                        raise WorkpieceWriteError(
                            f"Could not update paint workpiece '{storage_id}': {exc}; "
                            f"thumbnail rollback failed: {rollback_exc}. Record is blocked; recovery files: {staging}"
                        ) from exc
                raise WorkpieceWriteError(f"Could not update paint workpiece '{storage_id}': {exc}") from exc
            finally:
                if not preserve_staging:
                    if marker_created and os.path.exists(marker):
                        try:
                            os.unlink(marker)
                        except OSError as exc:
                            raise WorkpieceWriteError(
                                f"Paint workpiece '{storage_id}' remains blocked because publication cleanup failed: {exc}; recovery files: {staging}"
                            ) from exc
                    self._discard_staging(staging)
            return path

    def load_raw(self, storage_id: str) -> Optional[dict]:
        with self._lock:
            path = self._find_file(storage_id)
            if path is None:
                return None
            with open(path, "r", encoding="utf-8") as handle:
                return json.load(handle)

    def _build_path(self) -> str:
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        storage_id = now.strftime("%Y-%m-%d_%H-%M-%S-%f")
        folder = os.path.join(self._root, date_str, storage_id)
        self._assert_safe_path(folder)
        os.makedirs(os.path.dirname(folder), exist_ok=True)
        return os.path.join(folder, f"{storage_id}_workpiece.json")

    def _find_file(self, storage_id: str) -> Optional[str]:
        self._validate_storage_id(storage_id)
        for date_dir in os.listdir(self._root):
            candidate = os.path.join(self._root, date_dir, storage_id, f"{storage_id}_workpiece.json")
            if os.path.lexists(candidate):
                self._assert_safe_path(candidate)
                self._assert_safe_path(os.path.join(os.path.dirname(candidate), ".incomplete"))
                if os.path.exists(os.path.join(os.path.dirname(candidate), ".incomplete")):
                    raise WorkpieceWriteError(f"Paint workpiece '{storage_id}' is blocked by an incomplete update; recovery is required")
                return candidate
        return None
