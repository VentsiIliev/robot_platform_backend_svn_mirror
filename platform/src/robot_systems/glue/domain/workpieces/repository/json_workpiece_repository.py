import logging
import os
import shutil
from pathlib import Path
from src.engine.core.durable_files import atomic_write_json, atomic_write_bytes, ensure_directory, sync_directory
from src.engine.repositories.json.json_store import read_json_object
from datetime import datetime
from typing import List, Optional

import numpy as np

from src.applications.workpiece_library.workpiece_thumbnail import (
    generate_thumbnail_bytes,
)
from src.robot_systems.glue.domain.workpieces.model.glue_workpiece import GlueWorkpiece
from src.robot_systems.glue.domain.workpieces.repository.i_workpiece_repository import IWorkpieceRepository

_logger = logging.getLogger(__name__)


def _numpy_to_python(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: _numpy_to_python(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_numpy_to_python(i) for i in obj]
    return obj


class JsonWorkpieceRepository(IWorkpieceRepository):

    def __init__(self, storage_root: str):
        self._root = os.path.abspath(storage_root)
        ensure_directory(Path(self._root))
        _logger.info("JsonWorkpieceRepository: root → %s", self._root)

    def save(self, workpiece) -> str:

        if isinstance(workpiece, dict):
            serialized = _numpy_to_python(workpiece)  # ← was: serialized = workpiece
        else:
            serialized = GlueWorkpiece.serialize(workpiece)

        file_path  = self._build_path()
        folder     = os.path.dirname(file_path)
        ts         = os.path.basename(folder)

        atomic_write_json(Path(file_path), serialized)
        _logger.info("Workpiece saved → %s", file_path)

        # generate thumbnail alongside the JSON
        thumb_path = os.path.join(folder, f"{ts}_thumbnail.png")
        thumb_bytes = generate_thumbnail_bytes(serialized)
        if thumb_bytes:
            atomic_write_bytes(Path(thumb_path), thumb_bytes)
            _logger.debug("Thumbnail saved → %s", thumb_path)

        return file_path

    def load(self, workpiece_id: str):
        path = self._find_file(workpiece_id)
        if path is None:
            _logger.warning("Workpiece '%s' not found", workpiece_id)
            return None
        data = read_json_object(Path(path))
        return GlueWorkpiece.deserialize(data)

    def list_all(self) -> List[dict]:
        results = []
        for date_dir in sorted(os.listdir(self._root)):
            date_path = os.path.join(self._root, date_dir)
            if not os.path.isdir(date_path):
                continue
            for ts_dir in sorted(os.listdir(date_path)):
                ts_path = os.path.join(date_path, ts_dir)
                if not os.path.isdir(ts_path):
                    continue
                file_path = os.path.join(ts_path, f"{ts_dir}_workpiece.json")
                if not os.path.exists(file_path):
                    continue
                try:
                    data = read_json_object(Path(file_path))
                    thumb_path = os.path.join(ts_path, f"{ts_dir}_thumbnail.png")
                    results.append({
                        "id":            ts_dir,
                        "name":          data.get("name", ""),
                        "date":          date_dir,
                        "path":          file_path,
                        "thumbnail_path": thumb_path if os.path.exists(thumb_path) else None,
                    })
                except Exception as exc:
                    _logger.error("Could not read workpiece at %s: %s", file_path, exc)
                    raise
        return results

    def get_thumbnail_bytes(self, workpiece_id: str) -> Optional[bytes]:
        """Return PNG bytes for the workpiece thumbnail, generating lazily if missing."""
        for date_dir in os.listdir(self._root):
            folder = os.path.join(self._root, date_dir, workpiece_id)
            if not os.path.isdir(folder):
                continue
            thumb_path = os.path.join(folder, f"{workpiece_id}_thumbnail.png")
            json_path  = os.path.join(folder, f"{workpiece_id}_workpiece.json")

            if os.path.exists(thumb_path):
                with open(thumb_path, "rb") as f:
                    return f.read()

            # lazy generation for workpieces saved before thumbnails were introduced
            if os.path.exists(json_path):
                _logger.debug("Generating thumbnail lazily for %s", workpiece_id)
                raw = read_json_object(Path(json_path))
                thumb_bytes = generate_thumbnail_bytes(raw)
                if thumb_bytes:
                    atomic_write_bytes(Path(thumb_path), thumb_bytes)
                return thumb_bytes
        return None

    def delete(self, workpiece_id: str) -> bool:
        path = self._find_file(workpiece_id)
        if path is None:
            return False
        folder = os.path.dirname(path)
        try:
            shutil.rmtree(folder)
            sync_directory(Path(folder).parent)
            _logger.info("Deleted workpiece folder: %s", folder)
            return True
        except Exception as exc:
            _logger.error("Failed to delete '%s': %s", workpiece_id, exc)
            return False

    def _build_path(self) -> str:
        now      = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        ts_str   = now.strftime("%Y-%m-%d_%H-%M-%S-%f")
        folder   = os.path.join(self._root, date_str, ts_str)
        ensure_directory(Path(folder))
        return os.path.join(folder, f"{ts_str}_workpiece.json")

    def _find_file(self, workpiece_id: str) -> Optional[str]:
        for date_dir in os.listdir(self._root):
            candidate = os.path.join(
                self._root, date_dir, workpiece_id, f"{workpiece_id}_workpiece.json"
            )
            if os.path.exists(candidate):
                return candidate
        return None

    def workpiece_id_exists(self, workpiece_id: str) -> bool:
        for meta in self.list_all():
            path = meta.get("path")
            if not path:
                continue
            try:
                raw = read_json_object(Path(path))
                if str(raw.get("workpieceId", "")) == str(workpiece_id):
                    return True
            except Exception:
                _logger.exception("Could not check workpiece identity at %s", path)
                raise
        return False

    def update(self, storage_id: str, data: dict) -> str:
        path = self._find_file(storage_id)
        if path is None:
            raise FileNotFoundError(f"Workpiece '{storage_id}' not found")
        serialized = _numpy_to_python(data) if isinstance(data, dict) else GlueWorkpiece.serialize(data)
        atomic_write_json(Path(path), serialized)
        _logger.info("Workpiece updated → %s", path)

        folder     = os.path.dirname(path)
        thumb_path = os.path.join(folder, f"{storage_id}_thumbnail.png")
        thumb_bytes = generate_thumbnail_bytes(serialized)
        if thumb_bytes:
            atomic_write_bytes(Path(thumb_path), thumb_bytes)
        return path
