from __future__ import annotations

import logging
from time import perf_counter

from src.engine.robot.motion_sequence import OrderedMotionType
from src.engine.robot.path_preparation import WorkpieceExecutionPlan
from src.robot_systems.paint.diagnostics.trajectory import elapsed_s
from src.robot_systems.paint.processes.paint.configuration.models import DropoffStrategy
from .plan import IDropoffWaypointPlanner
from .strategies.movement_group import MovementGroupDropoffPlanner
from src.robot_systems.paint.processes.paint.motion.pose_comparison import poses_close
from src.robot_systems.paint.timing import timed_step

_logger = logging.getLogger(__name__)


class DropoffWaypointExecutor:
    """Execute a waypoint plan; lifecycle strategies own preparation and release."""

    def __init__(self, owner, planner: IDropoffWaypointPlanner | None = None) -> None:
        self._owner = owner
        self._planner_override = planner
        self._planners: dict[DropoffStrategy, IDropoffWaypointPlanner] = {
            MovementGroupDropoffPlanner.name: MovementGroupDropoffPlanner(),
        }

    def _resolve_planner(self) -> IDropoffWaypointPlanner | None:
        if self._planner_override is not None:
            return self._planner_override
        strategy_name = self._owner._paint_process_config().dropoff.strategy
        return self._planners.get(strategy_name)

    @timed_step(_logger, "pre_release_dropoff")
    def execute(self, execution_plan: WorkpieceExecutionPlan) -> tuple[bool, str]:
        """Execute the dropoff plan and release the workpiece at its release waypoint."""
        started = perf_counter()
        strategy = self._resolve_planner()
        if strategy is None:
            strategy_name = self._owner._paint_process_config().dropoff.strategy
            return False, f"Unknown paint dropoff strategy '{strategy_name}'"
        plan = strategy.build_plan(self._owner, execution_plan)
        release_count = sum(1 for waypoint in plan.waypoints if waypoint.release_here)
        if release_count != 1:
            if plan.strategy_name == MovementGroupDropoffPlanner.name:
                return False, "Dropoff movement group 'Dropoff' is not configured"
            return False, f"Dropoff strategy '{plan.strategy_name}' must define exactly one release waypoint"

        _logger.info(
            "[DROPOFF] executing strategy=%s waypoints=%d",
            plan.strategy_name,
            len(plan.waypoints),
        )
        for index, waypoint in enumerate(plan.waypoints, start=1):
            waypoint_started = perf_counter()
            if waypoint.pose is not None:
                already_at_release_pose = (
                    bool(self._owner._dropoff_unwind_prepared)
                    and waypoint.release_here
                    and poses_close(waypoint.pose, self._owner._last_process_end_pose)
                )
                if already_at_release_pose:
                    _logger.info(
                        "[DROPOFF] waypoint '%s' already completed by ordered cleanup chain; releasing in place",
                        waypoint.label,
                    )
                elif not self._owner._motion.move_pickup_phase(
                    waypoint.label,
                    list(waypoint.pose),
                    velocity=waypoint.vel_percent,
                    acceleration=waypoint.acc_percent,
                    motion_type=(
                        OrderedMotionType.LINEAR
                        if waypoint.corridor_id
                        else waypoint.motion_type
                    ),
                    blendR=waypoint.blendR,
                    corridor_id=waypoint.corridor_id,
                ):
                    _logger.debug(
                        "[TIMING] pre_release_dropoff success=false strategy=%s waypoint=%d label=%s elapsed_s=%.3f total_elapsed_s=%.3f",
                        plan.strategy_name,
                        index,
                        waypoint.label,
                        elapsed_s(waypoint_started),
                        elapsed_s(started),
                    )
                    return False, f"Pivot paint finished, but dropoff waypoint '{waypoint.label}' failed before release"

            if waypoint.release_here:
                ok, msg = self._owner._vacuum.turn_vacuum_off()
                if not ok:
                    _logger.debug(
                        "[TIMING] pre_release_dropoff success=false strategy=%s waypoint=%d stage=release elapsed_s=%.3f total_elapsed_s=%.3f",
                        plan.strategy_name,
                        index,
                        elapsed_s(waypoint_started),
                        elapsed_s(started),
                    )
                    return False, msg

        _logger.info(
            "[DROPOFF] strategy=%s completed elapsed_s=%.3f",
            plan.strategy_name,
            elapsed_s(started),
        )
        return True, ""
