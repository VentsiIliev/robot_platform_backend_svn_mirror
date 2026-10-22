from __future__ import annotations

from pathlib import Path
from typing import List

from src.engine.core.durable_files import atomic_write_json, sync_directory, ensure_directory
from src.engine.repositories.json.json_store import read_json_object

from src.robot_systems.twin_robot.domain import ChoreographyDefinition


class ChoreographyRepository:
    """Simple JSON repository owned by the twin robot system."""

    def __init__(self, root_dir: str):
        self._root = Path(root_dir)
        ensure_directory(self._root)

    def _path(self, choreography_id: str) -> Path:
        safe = "".join(c for c in str(choreography_id).strip() if c.isalnum() or c in {"-", "_"})
        if not safe:
            raise ValueError("Invalid choreography ID")
        return self._root / f"{safe}.json"

    def list(self) -> List[ChoreographyDefinition]:
        result: List[ChoreographyDefinition] = []
        for path in sorted(self._root.glob("*.json")):
            result.append(self._load_path(path))
        return result

    def get(self, choreography_id: str) -> ChoreographyDefinition:
        path = self._path(choreography_id)
        if not path.exists():
            raise FileNotFoundError(str(path))
        return self._load_path(path)

    def save(self, choreography: ChoreographyDefinition) -> None:
        path = self._path(choreography.choreography_id)
        atomic_write_json(path, choreography.to_dict())

    def delete(self, choreography_id: str) -> None:
        path = self._path(choreography_id)
        if path.exists():
            path.unlink()
            sync_directory(path.parent)

    @staticmethod
    def _load_path(path: Path) -> ChoreographyDefinition:
        return ChoreographyDefinition.from_dict(read_json_object(path))
