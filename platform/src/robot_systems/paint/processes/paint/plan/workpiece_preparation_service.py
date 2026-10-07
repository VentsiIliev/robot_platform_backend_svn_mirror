from __future__ import annotations

import copy
import logging
from typing import Callable, Optional

from src.robot_systems.paint.processes.paint.align import (
    _normalize_contour_points,
)
from src.robot_systems.paint.processes.paint.plan.contour_utils import (
    contour_to_workpiece_raw,
    describe_contour,
    extract_points_for_log,
)

from src.robot_systems.paint.processes.paint.match.results import (
    MatchResult, NoMatch, PreparationResult, PreparedWorkpiece,
)
from src.robot_systems.paint.processes.paint.results import (
    Failed, Ready, PaintFailure, PaintFailureCode,
)

_logger = logging.getLogger(__name__)

class PaintWorkpiecePreparationService:
    """Prepare the raw workpiece payload that paint production should execute."""
    def __init__(
        self,
        *,
        can_match_fn: Callable[[], bool],
        match_workpiece_fn: Callable,
        typed_match_workpiece_fn: Callable[[object], MatchResult] | None = None,
        default_settings: Optional[dict] = None,
        default_settings_getter: Optional[Callable[[], dict]] = None,
        transformer=None,
        transformer_getter: Optional[Callable[[], object]] = None,
    ) -> None:
        """Store matching hooks and the transformer needed for contour preparation."""
        self._can_match_fn = can_match_fn
        self._match_workpiece_fn = match_workpiece_fn
        self._typed_match_workpiece_fn = typed_match_workpiece_fn
        self._default_settings = dict(default_settings or {})
        self._default_settings_getter = default_settings_getter
        self._transformer = transformer
        self._transformer_getter = transformer_getter

    def _current_transformer(self):
        if self._transformer_getter is not None:
            return self._transformer_getter()
        return self._transformer

    def prepare_workpiece(
        self, captured_contour, frame, *, enable_matching: bool = True,
        default_settings_override: Optional[dict] = None,
    ) -> tuple[dict | None, str]:
        """Legacy adapter; production consumes prepare_result."""
        result = self.prepare_result(captured_contour, frame, enable_matching=enable_matching,
                                     default_settings_override=default_settings_override)
        if isinstance(result, Ready):
            return result.value.raw, result.value.description
        if isinstance(result, Failed):
            return None, result.failure.message
        return None, "Unknown workpiece"

    def prepare_result(
        self, captured_contour, frame, *, enable_matching: bool = True,
        default_settings_override: Optional[dict] = None,
    ) -> PreparationResult:
        """Preserve matching failure categories; absence is a separate result."""
        try:
            if enable_matching and self._can_match_fn():
                if self._typed_match_workpiece_fn is not None:
                    matched = self._typed_match_workpiece_fn(captured_contour)
                    if isinstance(matched, (Failed, NoMatch)):
                        return matched
                    payload = matched.value.as_editor_payload()
                else:
                    # Existing integrations may still inject the shared editor tuple contract.
                    ok, payload, message = self._match_workpiece_fn(captured_contour)
                    if not ok or not payload:
                        return NoMatch(message or "No match found")
                raw = self._build_matched_workpiece_raw(payload, captured_contour, frame)
                if raw is None:
                    return Failed(PaintFailure(PaintFailureCode.MATCHING, "prepare_matched_workpiece",
                                               "Matched workpiece has no executable contour"))
                label = payload.get("workpieceId") or payload.get("name") or "matched workpiece"
                return Ready(PreparedWorkpiece(raw, f"Executed {label}"))
            # Preserve the existing disabled/unavailable matching fallback policy.
            settings = (dict(default_settings_override) if default_settings_override is not None
                        else self._current_default_settings())
            raw = contour_to_workpiece_raw(captured_contour, workpiece_id="captured",
                                          name="Captured contour", default_settings=settings)
            return Ready(PreparedWorkpiece(raw, "Executed captured contour"))
        except OSError as exc:
            _logger.exception("[PREP] Failed to prepare workpiece")
            return Failed(PaintFailure(PaintFailureCode.STORAGE, "workpiece_preparation", str(exc)))
        except Exception as exc:
            _logger.exception("[PREP] Unexpected workpiece preparation failure")
            return Failed(PaintFailure(PaintFailureCode.INTERNAL, "workpiece_preparation", str(exc)))

    def _current_default_settings(self) -> dict:
        if self._default_settings_getter is None:
            return dict(self._default_settings)
        return dict(self._default_settings_getter() or {})

    def _build_matched_workpiece_raw(self, payload: dict, captured_contour, frame) -> dict | None:
        """Build an executable raw workpiece from matched storage data and the live contour."""
        matched_raw = copy.deepcopy(payload.get("raw") or {})
        if not matched_raw:
            return None

        if matched_raw.get("contour"):
            _logger.info(
                "[PREP] branch=contour workpiece_id=%s source=%s captured=%s",
                str(matched_raw.get("workpieceId") or matched_raw.get("name") or ""),
                describe_contour(extract_points_for_log(matched_raw)),
                describe_contour(_normalize_contour_points(captured_contour)),
            )
            return matched_raw

        _logger.info(
            "[PREP] matched workpiece has no saved contour; falling back to captured contour"
        )
        return None

    @staticmethod
    def _resolve_frame_size(frame) -> tuple[float, float]:
        """Extract image height and width from a captured frame with safe defaults."""
        if frame is None:
            return 720.0, 1280.0
        try:
            return float(frame.shape[0]), float(frame.shape[1])
        except Exception:
            _logger.debug("Failed to read frame shape", exc_info=True)
            return 720.0, 1280.0
