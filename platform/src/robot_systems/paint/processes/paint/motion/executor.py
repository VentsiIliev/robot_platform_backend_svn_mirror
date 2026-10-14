from __future__ import annotations

import logging
from typing import Callable
from src.engine.robot.interfaces.i_robot_service import IRobotService
from dataclasses import replace
from src.engine.robot.motion_sequence import OrderedMotionCommand, OrderedMotionType, OrderedPathCommand, OrderedPositionCommand
from src.robot_systems.paint.timing import timed_step
from src.robot_systems.paint.processes.paint.motion.recovery import PaintMotionRecovery

_logger = logging.getLogger(__name__)


class PaintMotionExecutor:
    """Submit individual robot moves and ordered sequences."""

    def __init__(self, robot_service: IRobotService, *, tool_provider: Callable[[], int], user_provider: Callable[[], int], recovery: PaintMotionRecovery, command_recorder: Callable[[dict], None] | None = None) -> None:
        self._robot_service = robot_service
        self._tool_provider = tool_provider
        self._user_provider = user_provider
        self._recovery = recovery
        self._command_recorder = command_recorder
        self.last_motion_error: str | None = None

    @timed_step(_logger, "pickup_phase", label_arg="label")
    def move_pickup_phase(
        self,
        label: str,
        pose: list[float],
        *,
        velocity: float,
        acceleration: float,
        motion_type: OrderedMotionType = OrderedMotionType.PTP,
        blendR: float = 0.0,
        corridor_id: str | None = None,
    ) -> bool:
        """Execute one carried-workpiece robot move with explicit motion limits."""
        if velocity is None or acceleration is None:
            raise ValueError(f"Pickup phase '{label}' requires explicit velocity and acceleration")
        if not isinstance(motion_type, OrderedMotionType):
            raise TypeError("motion_type must be an OrderedMotionType")
        self._record({
            "kind": "single_move", "label": label, "type": motion_type.value,
            "position": list(pose), "vel": float(velocity), "acc": float(acceleration),
            "blendR": float(blendR), "corridor_id": corridor_id,
        })
        _logger.info(
            "[PICKUP] %s tool=%d user=%d pose=%s",
            label,
            self._tool_provider(),
            self._user_provider(),
            [round(v, 3) for v in pose],
        )
        while True:
            if corridor_id is not None:
                ok = self._robot_service.move_linear_in_corridor(
                    corridor_id=corridor_id,
                    position=pose,
                    tool=self._tool_provider(),
                    user=self._user_provider(),
                    velocity=velocity,
                    acceleration=acceleration,
                    blendR=max(0.0, float(blendR)),
                    wait_to_reach=True,
                )
            elif motion_type is OrderedMotionType.FAST_LINEAR:
                result = self._robot_service.move_fast_linear(
                    position=pose,
                    tool=self._tool_provider(),
                    user=self._user_provider(),
                    vel=velocity,
                    acc=acceleration,
                    trajectory_optimizer="TOTG",
                )
                ok = bool(
                    isinstance(result, dict)
                    and result.get("result") == 0
                    and result.get("success") is True
                    and result.get("accepted") is True
                    and result.get("final") is True
                    and result.get("queued") is False
                )
            elif motion_type is OrderedMotionType.LINEAR:
                ok = self._robot_service.move_linear(
                    position=pose,
                    tool=self._tool_provider(),
                    user=self._user_provider(),
                    velocity=velocity,
                    acceleration=acceleration,
                    blendR=max(0.0, float(blendR)),
                    wait_to_reach=True,
                )
            else:
                ok = self._robot_service.move_ptp(
                    position=pose,
                    tool=self._tool_provider(),
                    user=self._user_provider(),
                    velocity=velocity,
                    acceleration=acceleration,
                    wait_to_reach=True,
                )
            if ok:
                return True
            if not self._recovery.resume_after_interrupted_non_contact_motion(label):
                return False

    @timed_step(_logger, "pickup_phase", label_arg="label")
    def move_ordered_pickup_sequence(self, label: str, segments: list[OrderedMotionCommand]) -> bool:
        """Execute a pickup sequence as ordered robot motion segments."""
        _logger.info(
            "[PICKUP] %s tool=%d user=%d segments=%d",
            label,
            self._tool_provider(),
            self._user_provider(),
            len(segments),
        )
        self.record_ordered_chain(label, segments)
        if any(
            isinstance(segment, OrderedPositionCommand)
            and segment.motion_type is OrderedMotionType.FAST_LINEAR
            for segment in segments
        ):
            return self._move_mixed_pickup_sequence(label, segments)
        active_segments = list(segments)
        while active_segments:
            result = self._robot_service.execute_ordered_motion_chain(
                segments=active_segments,
                tool=self._tool_provider(),
                user=self._user_provider(),
                blocking=True,
            )
            if isinstance(result, int) and not isinstance(result, bool) and result == 0:
                self.last_motion_error = None
                return True
            self.last_motion_error = self._robot_service.get_last_motion_error()
            if self.last_motion_error:
                _logger.error("[PICKUP] Ordered motion chain rejected: %s", self.last_motion_error)
            if not self._recovery.resume_after_interrupted_non_contact_motion(label):
                return False
            active_segments = self._recovery.trim_ordered_pickup_segments_from_current_pose(active_segments)
        return True

    def _move_mixed_pickup_sequence(self, label: str, segments: list[OrderedMotionCommand]) -> bool:
        """Execute ordered-compatible chunks around explicit Fast LIN moves."""
        ordered_chunk: list[OrderedMotionCommand] = []

        def flush_ordered_chunk() -> bool:
            if not ordered_chunk:
                return True
            chunk = list(ordered_chunk)
            terminal = chunk[-1]
            if isinstance(terminal, (OrderedPositionCommand, OrderedPathCommand)):
                chunk[-1] = replace(
                    terminal,
                    profile=replace(terminal.profile, blend_radius=0.0),
                )
            ordered_chunk.clear()
            return self.move_ordered_pickup_sequence(f"{label} (ordered chunk)", chunk)

        for segment in segments:
            if not (
                isinstance(segment, OrderedPositionCommand)
                and segment.motion_type is OrderedMotionType.FAST_LINEAR
            ):
                ordered_chunk.append(segment)
                continue
            if not flush_ordered_chunk():
                return False
            if not self.move_pickup_phase(
                segment.label or label,
                list(segment.position),
                velocity=float(segment.profile.velocity_percent),
                acceleration=float(segment.profile.acceleration_percent),
                motion_type=OrderedMotionType.FAST_LINEAR,
                blendR=0.0,
            ):
                return False
        return flush_ordered_chunk()

    def record_ordered_chain(self, label: str, segments: list[OrderedMotionCommand]) -> None:
        """Record an exact ordered command payload before it reaches the robot."""
        self._record({
            "kind": "ordered_chain",
            "label": label,
            "commands": [segment.to_payload() for segment in segments],
        })

    def _record(self, payload: dict) -> None:
        if self._command_recorder is not None:
            self._command_recorder(payload)
