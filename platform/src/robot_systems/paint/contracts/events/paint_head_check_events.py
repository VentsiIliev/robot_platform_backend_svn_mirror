"""Typed, detector-independent inspection status for the paint dashboard."""

from dataclasses import dataclass
from enum import Enum, auto

from src.robot_systems.paint.contracts.paint_head_check.models import PaintHeadObservation
from src.robot_systems.paint.contracts.paint_head_check.results import HeadCheckEvidence


class PaintHeadFeedbackMode(Enum):
    CHECK = auto()
    LIVE_GUIDANCE = auto()
    GUIDANCE_ENDED = auto()


@dataclass(frozen=True, slots=True)
class PaintHeadCheckStatusEvent:
    revision: int
    evidence: HeadCheckEvidence | None
    previous_observation: PaintHeadObservation | None = None
    mode: PaintHeadFeedbackMode = PaintHeadFeedbackMode.CHECK

    @property
    def last_observation(self) -> PaintHeadObservation | None:
        """An acquisition failure does not reclassify the last detected head state."""
        if isinstance(self.evidence, PaintHeadObservation):
            return self.evidence
        return self.previous_observation if self.evidence is not None else None


class PaintHeadCheckTopics:
    STATUS = "paint/head-check/status"
    REQUEST_STATUS = "paint/head-check/request-status"
