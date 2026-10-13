"""Cycle and motion-plan contracts for interchangeable dropoff behavior."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Protocol, TYPE_CHECKING
from src.robot_systems.paint.contracts.next_cycle_target import NextCycleTarget

if TYPE_CHECKING:
    from src.engine.robot.motion_sequence import OrderedMotionCommand
    from src.engine.robot.path_preparation import WorkpieceExecutionPlan
    from src.robot_systems.paint.processes.paint.operations.pickup.executor import PickupPlan
    from src.robot_systems.paint.processes.paint.results import Ready, Failed, PaintOperationResult


@dataclass(frozen=True)
class DropoffResult:
    success: bool
    message: str = ""
    prepositioned_group: str | None = None
    tray_full: bool = False


@dataclass(frozen=True)
class DropoffCycleRequest:
    """Workpiece and pickup geometry plus lazy calibration-position access."""

    execution_plan: WorkpieceExecutionPlan
    pickup_plan: PickupPlan
    calibration_source: Callable[[], tuple[str, list[float] | None]]


@dataclass(frozen=True)
class DropoffApproach:
    """Commands contributed to a combined chain and their completion receipt.

    The workflow carries this record without interpreting destination-specific
    completion fields. Only the creating strategy commits that bookkeeping.
    """

    segments: tuple[OrderedMotionCommand, ...] = ()
    final_pose: list[float] | None = None
    prepares_release: bool = False
    completes_entry: bool = False


class IDropoffExecution(Protocol):
    """Preparation/release boundary used by production orchestration."""

    def prepare_dropoff(self) -> tuple[bool, str]:
        """Prepare remaining movements before verified release."""
        ...


    def release_dropoff(self, next_cycle_start: NextCycleTarget | None = None) -> DropoffResult:
        """Verify release and exit, preserving capacity/prepositioning outcomes."""
        ...


class IDropoffStrategy(IDropoffExecution, Protocol):
    """Own reservation, painting handoff, approach, release, and finalization."""

    def begin_cycle(self, request: DropoffCycleRequest) -> PaintOperationResult:
        """Reserve destination capacity before pickup, or return a typed refusal."""
        ...

    def painting_detach_pose(self, *, is_final_job: bool, paint_start_rz: float, paint_end_rz: float | None) -> list[float] | None:
        """Optionally supply the painting-to-destination handoff pose."""
        ...

    def plan_paint_approach(self, *, cleanup_pending: bool) -> Ready[DropoffApproach] | Failed:
        """Contribute destination approach commands after the paint path."""
        ...

    def plan_cleanup_approach(self, final_pose: list[float]) -> DropoffApproach:
        """Contribute destination approach commands after edge cleanup."""
        ...

    def activate_approach(self, approach: DropoffApproach) -> PaintOperationResult:
        """Establish required passage/hardware state before executing commands."""
        ...

    def approach_completed(self, approach: DropoffApproach) -> None:
        """Record successful execution so preparation is not repeated."""
        ...



    def finish_cycle(self, result: PaintOperationResult) -> None:
        """Finalize or cancel destination resources on every terminal path."""
        ...
