from __future__ import annotations

import logging
from typing import Callable
from src.engine.robot.interfaces.i_robot_service import IRobotService
from src.robot_systems.paint.processes.paint.production.execution_control import PaintExecutionControl
import numpy as np
from src.engine.robot.motion_sequence import OrderedMotionCommand, OrderedPathCommand, OrderedPositionCommand
from src.robot_systems.paint.processes.paint.motion.pose_sampling import FreshPoseReadError, read_fresh_pose

_logger = logging.getLogger(__name__)
_PICKUP_RESUME_WAYPOINT_TOLERANCE_MM = 2.0


class PaintMotionRecovery:
    """Track and resume interrupted non-contact robot movements."""

    def __init__(self, robot_service: IRobotService, control_provider: Callable[[], PaintExecutionControl | None]) -> None:
        self._robot_service = robot_service
        self._control_provider = control_provider
        self._ordered_chain_resume_start_index: int | None = None
        self._ordered_chain_interrupted_by_pause = False

    def pause_current_execution(self) -> None:
        control = self._control_provider()
        if control is not None and control.in_protected_phase():
            return
        ordered_status = self.read_ordered_motion_chain_status()
        if self.ordered_motion_chain_segment_is_protected(ordered_status):
            _logger.info("[EXECUTE] Paint pause requested during protected ordered segment; deferring stop")
            return
        self._ordered_chain_resume_start_index = self.ordered_motion_chain_resume_index(ordered_status)
        self._ordered_chain_interrupted_by_pause = True
        try:
            self._robot_service.stop_motion()
        except Exception:
            _logger.exception("[EXECUTE] Failed to stop robot motion during paint pause")
            raise

    def read_ordered_motion_chain_status(self) -> dict | None:
        try:
            status = self._robot_service.get_execution_status()
        except Exception:
            _logger.exception("[EXECUTE] Failed to read ordered motion status during paint pause")
            return None
        if not isinstance(status, dict):
            return None
        ordered = status.get("ordered_motion_chain")
        if not isinstance(ordered, dict):
            return None
        return ordered

    @staticmethod
    def ordered_motion_chain_segment_is_protected(ordered: dict | None) -> bool:
        if not isinstance(ordered, dict):
            return False
        return bool(
            ordered.get("active")
            and ordered.get("phase") == "executing"
            and ordered.get("current_segment_protected")
        )

    @staticmethod
    def ordered_motion_chain_resume_index(ordered: dict | None) -> int:
        if not isinstance(ordered, dict) or not ordered.get("active"):
            return 0
        try:
            index = int(ordered.get("current_segment_index"))
        except (TypeError, ValueError):
            return 0
        return max(0, index)

    def resume_after_interrupted_non_contact_motion(self, label: str) -> bool:
        control = self._control_provider()
        interrupted_by_pause = self._ordered_chain_interrupted_by_pause
        if (control is None or not control.pause_requested()) and not interrupted_by_pause:
            return False
        _logger.info("[EXECUTE] Paused during non-contact motion '%s'; waiting to resume", label)
        resumed = bool(control.wait_if_paused())
        if resumed:
            self._ordered_chain_interrupted_by_pause = False
        return resumed

    def consume_ordered_chain_resume_start_index(self) -> int | None:
        start_index = self._ordered_chain_resume_start_index
        self._ordered_chain_resume_start_index = None
        return start_index

    def mark_ordered_chain_interrupted_by_pause(self, interrupted: bool) -> None:
        self._ordered_chain_interrupted_by_pause = bool(interrupted)

    def trim_ordered_pickup_segments_from_current_pose(
        self,
        segments: list[OrderedMotionCommand],
    ) -> list[OrderedMotionCommand]:
        """Skip already-passed pickup waypoints after pause/resume."""
        if not segments:
            return []

        backend_index = self.consume_ordered_chain_resume_start_index()
        if backend_index is not None and 0 <= backend_index < len(segments):
            _logger.info(
                "[PICKUP] Resuming ordered sequence from backend segment %d/%d",
                backend_index + 1,
                len(segments),
            )
            return segments[backend_index:]
        if backend_index is not None:
            _logger.warning(
                "[PICKUP] Ignoring invalid backend resume segment %d for %d commands",
                backend_index,
                len(segments),
            )

        current = self._read_current_robot_pose()
        if current is None:
            _logger.warning("[PICKUP] Resume requested but current robot pose is unavailable; reusing full sequence")
            return segments

        indexed_targets: list[tuple[int, list[float]]] = []
        for command_index, segment in enumerate(segments):
            if isinstance(segment, OrderedPathCommand):
                indexed_targets.append((command_index, list(segment.path[-1])))
            elif isinstance(segment, OrderedPositionCommand):
                indexed_targets.append((command_index, list(segment.position)))
        if not indexed_targets:
            return segments

        current_xyz = np.asarray(current[:3], dtype=float)
        targets_xyz = [np.asarray(target[:3], dtype=float) for _, target in indexed_targets]

        best_index = min(
            range(len(targets_xyz)),
            key=lambda index: float(np.linalg.norm(current_xyz - targets_xyz[index])),
        )
        for index in range(
            max(0, best_index - 1),
            min(len(targets_xyz) - 1, best_index + 2),
        ):
            distance = self._point_to_segment_distance(
                current_xyz,
                targets_xyz[index],
                targets_xyz[index + 1],
            )
            if distance <= _PICKUP_RESUME_WAYPOINT_TOLERANCE_MM:
                best_index = index + 1
                break

        next_target_index = min(best_index + 1, len(indexed_targets) - 1)
        start_index = indexed_targets[next_target_index][0]
        _logger.info(
            "[PICKUP] Resuming ordered sequence from segment %d/%d current=%s",
            start_index + 1,
            len(segments),
            [round(float(value), 3) for value in current[:6]],
        )
        return segments[start_index:]

    def _read_current_robot_pose(self) -> list[float] | None:
        try:
            pose = read_fresh_pose(
                self._robot_service,
                error_message="Failed to read fresh robot pose for ordered resume",
            )
        except FreshPoseReadError as exc:
            _logger.error("[PICKUP] %s", exc)
            return None
        return pose

    @staticmethod
    def _point_to_segment_distance(point: np.ndarray, start: np.ndarray, end: np.ndarray) -> float:
        segment = end - start
        length_sq = float(np.dot(segment, segment))
        if length_sq <= 1e-12:
            return float(np.linalg.norm(point - start))
        t = float(np.dot(point - start, segment) / length_sq)
        t = max(0.0, min(1.0, t))
        projection = start + t * segment
        return float(np.linalg.norm(point - projection))
