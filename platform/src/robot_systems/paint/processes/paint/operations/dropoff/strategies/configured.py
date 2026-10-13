"""Dropoff strategies composed by the paint robot system."""
from __future__ import annotations
from src.robot_systems.paint.processes.paint.results import Ready, Failed, PaintOperationResult

from typing import TYPE_CHECKING
from src.robot_systems.paint.contracts.dropoff import IDropoffStrategy, DropoffResult, DropoffApproach, DropoffCycleRequest
from src.robot_systems.paint.contracts.next_cycle_target import NextCycleTarget
from src.robot_systems.paint.processes.paint.configuration.models import DropoffStrategy
from src.robot_systems.paint.processes.paint.operations.dropoff import motion

if TYPE_CHECKING:
    from src.robot_systems.paint.processes.paint.production.execution_runtime import PaintExecutionRuntime


from .movement_group import MovementGroupDropoff
from .plate_layout import PlateLayoutDropoff


class ConfiguredDropoffStrategy(IDropoffStrategy):
    """Select a built-in strategy from the runtime's cycle configuration.

    The cycle override used by alternating drying remains authoritative. A
    custom strategy can be injected directly instead of using this selector.
    """

    def __init__(self, runtime: PaintExecutionRuntime) -> None:
        self._runtime = runtime
        self._cycle_strategy: IDropoffStrategy | None = None
        self._strategies: dict[DropoffStrategy, IDropoffStrategy] = {
            DropoffStrategy.MOVEMENT_GROUP: MovementGroupDropoff(runtime),
            DropoffStrategy.PLATE_LAYOUT: PlateLayoutDropoff(runtime),
        }

    @property
    def name(self) -> DropoffStrategy:
        """Expose the selected built-in identity to legacy shared pose resolvers."""
        selected = self._selected()
        return next(name for name, strategy in self._strategies.items() if strategy is selected)

    def _selected(self) -> IDropoffStrategy:
        if self._cycle_strategy is not None:
            return self._cycle_strategy
        name = self._runtime._paint_process_config().dropoff.strategy
        try:
            return self._strategies[name]
        except KeyError:
            raise ValueError(f"Unknown paint dropoff strategy '{name}'") from None

    def prepare_dropoff(self) -> tuple[bool, str]:
        return self._selected().prepare_dropoff()

    def release_dropoff(self, next_cycle_start: NextCycleTarget | None = None) -> DropoffResult:
        return self._selected().release_dropoff(next_cycle_start)


    def begin_cycle(self, request: DropoffCycleRequest) -> PaintOperationResult:
        self._cycle_strategy = self._selected()
        return self._cycle_strategy.begin_cycle(request)

    def painting_detach_pose(self, *, is_final_job: bool, paint_start_rz: float, paint_end_rz: float | None) -> list[float] | None:
        return self._selected().painting_detach_pose(is_final_job=is_final_job,
                  paint_start_rz=paint_start_rz, paint_end_rz=paint_end_rz)

    def plan_paint_approach(self, *, cleanup_pending: bool) -> Ready[DropoffApproach] | Failed:
        return self._selected().plan_paint_approach(cleanup_pending=cleanup_pending)

    def plan_cleanup_approach(self, final_pose: list[float]) -> DropoffApproach:
        return self._selected().plan_cleanup_approach(final_pose)

    def activate_approach(self, approach: DropoffApproach) -> PaintOperationResult:
        return self._selected().activate_approach(approach)

    def approach_completed(self, approach: DropoffApproach) -> None:
        self._selected().approach_completed(approach)

    def finish_cycle(self, result: PaintOperationResult) -> None:
        try:
            self._selected().finish_cycle(result)
        finally:
            self._cycle_strategy = None
