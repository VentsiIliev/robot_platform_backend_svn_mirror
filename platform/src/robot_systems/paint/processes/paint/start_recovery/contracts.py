"""Contracts for paint-specific routing before production navigation."""
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass

from src.engine.robot.motion_sequence import OrderedPositionCommand
from src.robot_systems.paint.contracts.next_cycle_target import NextCycleTarget
from src.robot_systems.paint.processes.paint.configuration.models import PaintDropoffConfig


@dataclass(frozen=True)
class StartRecoveryRequest:
    pose: tuple[float, ...]
    corners: tuple[tuple[float, ...], ...]
    dropoff: PaintDropoffConfig
    target_provider: Callable[[], NextCycleTarget | None]


class IStartRecoveryStrategy(ABC):
    """Select and build motion only; never release a workpiece or change tray state."""

    @abstractmethod
    def matches(self, request: StartRecoveryRequest) -> bool:
        """Whether this strategy owns the current position."""

    @abstractmethod
    def build_route(self, request: StartRecoveryRequest) -> list[OrderedPositionCommand]:
        """Return the required ordered route, or raise StartRecoveryError if unavailable."""
