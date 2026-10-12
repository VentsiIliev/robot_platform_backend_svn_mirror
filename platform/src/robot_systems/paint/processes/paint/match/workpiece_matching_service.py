from __future__ import annotations

import logging
from time import monotonic
from src.engine.diagnostics.events import observe
from typing import Callable, Optional

from src.applications.workpiece_editor.i_workpiece_matcher import IWorkpieceMatcher
from src.engine.vision.i_capture_snapshot_service import VisionCaptureSnapshot
from src.robot_systems.paint.processes.paint.match.matchable_workpiece import MatchableWorkpiece

from .results import MatchedWorkpiece, MatchResult, NoMatch
from src.robot_systems.paint.processes.paint.results import Failed, Ready, PaintFailure, PaintFailureCode

_logger = logging.getLogger(__name__)

class PaintWorkpieceMatchingService(IWorkpieceMatcher):
    """Adapt paint workpiece storage to the shared contour-matching interface."""
    def __init__(
        self,
        *,
        list_saved_workpieces_fn: Optional[Callable[[], list[dict]]] = None,
        load_saved_workpiece_fn: Optional[Callable[[str], Optional[dict]]] = None,
        selected_workpiece_ids_fn: Optional[Callable[[], tuple[str, ...] | None]] = None,
        run_matching_fn: Optional[Callable[[list, list], tuple]] = None,
        capture_snapshot_service=None,
        debug_dump_dir: str | None = None,
    ) -> None:
        """Store repository, matching, and snapshot dependencies for paint matching."""
        self._list_saved_workpieces_fn = list_saved_workpieces_fn
        self._load_saved_workpiece_fn = load_saved_workpiece_fn
        self._selected_workpiece_ids_fn = selected_workpiece_ids_fn
        self._run_matching_fn = run_matching_fn
        self._capture_snapshot_service = capture_snapshot_service
        self._debug_dump_dir = debug_dump_dir
        self._last_snapshot: VisionCaptureSnapshot | None = None

    def can_match_saved_workpieces(self) -> bool:
        """Report whether all dependencies needed for saved-workpiece matching are available."""
        return (
            callable(self._list_saved_workpieces_fn)
            and callable(self._load_saved_workpiece_fn)
            and callable(self._run_matching_fn)
        )

    def match_saved_workpieces(self, contour) -> tuple[bool, dict | None, str]:
        """Shared editor compatibility adapter; production consumes match_result."""
        result = self.match_result(contour)
        if isinstance(result, Ready):
            return True, result.value.as_editor_payload(), "Matched workpiece."
        if isinstance(result, Failed):
            return False, None, result.failure.message
        return False, None, result.message

    def match_result(self, contour) -> MatchResult:
        started = monotonic()
        result = self._match_result(contour)
        outcome = "matched" if isinstance(result, Ready) else "failed" if isinstance(result, Failed) else "unmatched"
        fields = {"outcome": outcome, "duration_s": monotonic() - started}
        if isinstance(result, Ready):
            fields.update(workpiece_id=result.value.workpiece_id,
                          storage_id=result.value.storage_id,
                          candidate_count=result.value.candidate_count,
                          confidence=result.value.confidence)
        elif isinstance(result, NoMatch):
            fields.update(candidate_count=result.candidate_count, message=result.message)
        else:
            fields.update(failure_code=result.failure.code.value, failure_stage=result.failure.stage)
        observe(_logger, "vision.match.ended",
                level=logging.ERROR if isinstance(result, Failed) else logging.INFO,
                metrics={f"vision.match.{outcome}": 1,
                         "vision.match.duration_seconds": monotonic() - started}, **fields)
        return result

    def _match_result(self, contour) -> MatchResult:
        if not self.can_match_saved_workpieces():
            return Failed(PaintFailure(PaintFailureCode.UNAVAILABLE, "matching",
                                       "Matching is not available in this editor."))
        stage = "load_matching_candidates"
        try:
            candidates = self._load_candidates()
            if not candidates:
                return NoMatch("No saved workpieces available.")
            stage = "match_contour"
            result, no_match_count, _matched_contours, _unmatched_contours = self._run_matching_fn(
                candidates, [contour],
            )
            workpieces = list((result or {}).get("workpieces", []))
            confidences = list((result or {}).get("mlConfidences", []))
            self._save_match_diagnostics(contour, candidates, matched=bool(workpieces))
            if not workpieces:
                return NoMatch(f"No match found. Saved workpieces checked: {len(candidates)}",
                               len(candidates))
            stage = "convert_matched_workpiece"
            best = workpieces[0]
            raw = best.to_raw()
            if not raw:
                return Failed(PaintFailure(PaintFailureCode.MATCHING, stage,
                                           "Matched workpiece could not be converted."))
            return Ready(MatchedWorkpiece(
                raw, best.storage_id, best.workpieceId, best.name,
                len(candidates), int(no_match_count),
                float(confidences[0]) if confidences else None,
            ))
        except (ValueError, UnicodeError) as exc:
            if stage != "load_matching_candidates":
                _logger.exception("Unexpected matcher validation failure stage=%s", stage)
                return Failed(PaintFailure(PaintFailureCode.INTERNAL, stage, str(exc)))
            _logger.exception("Saved workpiece data could not be read")
            return Failed(PaintFailure(PaintFailureCode.STORAGE, stage, str(exc)))
        except OSError as exc:
            _logger.exception("Paint workpiece matching I/O failed stage=%s", stage)
            return Failed(PaintFailure(PaintFailureCode.STORAGE if stage == "load_matching_candidates"
                                       else PaintFailureCode.MATCHING, stage, str(exc)))
        except Exception as exc:
            # Public matching boundary: preserve unexpected errors as INTERNAL, never NoMatch.
            _logger.exception("Paint workpiece matching failed stage=%s", stage)
            return Failed(PaintFailure(PaintFailureCode.INTERNAL, stage, str(exc)))

    def _save_match_diagnostics(self, contour, candidates: list, *, matched: bool) -> None:
        if not self._debug_dump_dir:
            return
        try:
            from src.robot_systems.paint.processes.paint.match.matching_diagnostics import (
                save_matching_diagnostics,
            )

            path = save_matching_diagnostics(
                self._debug_dump_dir,
                contour,
                candidates,
                matched=matched,
            )
            _logger.info("[MATCH_DEBUG] Saved workpiece matching diagnostics: %s", path)
        except Exception:
            _logger.exception("[MATCH_DEBUG] Failed to save workpiece matching diagnostics")

    def run_matching(self):
        """Run full-scene matching using a fresh snapshot, mirroring the shared matching workflow."""
        if self._capture_snapshot_service is None:
            return {}, 0, [], []
        snapshot = self._capture_snapshot_service.capture_snapshot(source="matching")
        self._last_snapshot = snapshot
        contours = list(snapshot.contours or [])
        if len(contours) == 0:
            _logger.debug("No contours found -> Skipping matching")
            return {}, 0, [], []

        candidates = self._load_candidates()
        if len(candidates) == 0:
            _logger.debug("No workpieces found -> Skipping matching")
            return {}, 0, [], []

        return self._run_matching_fn(candidates, contours)

    def get_last_capture_snapshot(self):
        """Return the most recent snapshot captured during a matching run."""
        return self._last_snapshot

    def _load_candidates(self) -> list:
        """Load saved workpieces and wrap them in the contour-matcher adapter shape."""
        selected_ids = (
            self._selected_workpiece_ids_fn()
            if self._selected_workpiece_ids_fn is not None else None
        )
        stored_ids = (
            selected_ids if selected_ids is not None
            else (item.get("id") for item in (self._list_saved_workpieces_fn() or []))
        )
        candidates: list[MatchableWorkpiece] = []
        for storage_id in stored_ids:
            if not storage_id:
                continue
            raw = self._load_saved_workpiece_fn(storage_id)
            if not raw or not raw.get("contour"):
                continue
            candidates.append(MatchableWorkpiece(raw, storage_id=storage_id))
        return candidates
