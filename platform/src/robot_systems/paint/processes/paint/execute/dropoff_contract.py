"""Public dropoff boundary between production orchestration and motion execution."""
from dataclasses import dataclass
from typing import Protocol

from src.robot_systems.paint.processes.paint.next_cycle_target import NextCycleTarget


@dataclass(frozen=True)
class DropoffResult:
    success: bool
    message: str = ""
    prepositioned_group: str | None = None
    tray_full: bool = False


class DropoffExecutor(Protocol):
    def prepare_dropoff(self) -> tuple[bool, str]:
        """Prepare the held workpiece for its configured destination."""
        ...

    def release_dropoff(self, next_cycle_start: NextCycleTarget | None = None) -> DropoffResult:
        """Run release and exit motion, returning placement and prepositioning status."""
        ...
