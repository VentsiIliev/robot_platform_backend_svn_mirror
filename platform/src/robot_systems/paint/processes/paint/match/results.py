"""Matching/preparation contracts used by production, with legacy editor adapters."""
from dataclasses import dataclass
from typing import TypeAlias

from src.robot_systems.paint.processes.paint.results import Failed, Ready


@dataclass(frozen=True)
class MatchedWorkpiece:
    raw: dict
    storage_id: str
    workpiece_id: str
    name: str
    candidate_count: int
    no_match_count: int
    confidence: float | None

    def as_editor_payload(self) -> dict:
        return {"raw": self.raw, "storage_id": self.storage_id,
                "workpieceId": self.workpiece_id, "name": self.name,
                "candidate_count": self.candidate_count, "no_match_count": self.no_match_count,
                "confidence": self.confidence}


@dataclass(frozen=True)
class NoMatch:
    message: str
    candidate_count: int = 0


@dataclass(frozen=True)
class PreparedWorkpiece:
    raw: dict
    description: str


MatchResult: TypeAlias = Ready[MatchedWorkpiece] | NoMatch | Failed
PreparationResult: TypeAlias = Ready[PreparedWorkpiece] | NoMatch | Failed
