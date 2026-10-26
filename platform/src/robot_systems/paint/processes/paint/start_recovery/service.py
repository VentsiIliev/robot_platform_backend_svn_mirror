"""Select one recovery strategy and execute it without direct-motion fallback."""
from collections.abc import Callable, Sequence
import logging
import math

from src.engine.robot.motion_sequence import OrderedPositionCommand
from src.robot_systems.paint.contracts.next_cycle_target import NextCycleTarget
from src.robot_systems.paint.processes.paint.configuration.models import DropoffStrategy, PaintDropoffConfig
from src.robot_systems.paint.processes.paint.tray_dry.plate_layout import validate_plate_corners
from .contracts import IStartRecoveryStrategy, StartRecoveryRequest
from .errors import (
    InvalidTrayGeometryError, NoRecoveryStrategyError, RecoveryInternalError,
    RecoveryMotionFailedError, RecoveryPoseUnavailableError, StartRecoveryError,
    TrayFrameMismatchError,
)
from .results import StartRecoveryOutcome, StartRecoveryResult
from .strategies import ContinueStartStrategy, TrayReturnRecoveryStrategy

_logger = logging.getLogger(__name__)


class StartRecoveryService:
    """Run a required regional return before allowing production to start."""

    def __init__(
        self, *, read_pose: Callable[[], list[float]],
        execute_route: Callable[[str, list[OrderedPositionCommand]], bool],
        strategies: Sequence[IStartRecoveryStrategy] | None = None,
    ) -> None:
        self._read_pose = read_pose
        self._execute_route = execute_route
        self._strategies = tuple(strategies) if strategies is not None else (
            TrayReturnRecoveryStrategy(), ContinueStartStrategy(),
        )

    def prepare(
        self, *, dropoff: PaintDropoffConfig,
        target_provider: Callable[[], NextCycleTarget | None],
        should_stop: Callable[[], bool], tool: int, user: int,
    ) -> StartRecoveryResult:
        """Return a typed outcome; expected errors retain their specific failure code."""
        try:
            return self._prepare(dropoff, target_provider, should_stop, tool, user)
        except StartRecoveryError as exc:
            _logger.warning("[START_RECOVERY] code=%s: %s", exc.failure.recovery_code, exc)
            return StartRecoveryResult(StartRecoveryOutcome.FAILED, exc.failure)
        except Exception as exc:
            _logger.exception("[START_RECOVERY] Unexpected recovery failure")
            return StartRecoveryResult(StartRecoveryOutcome.FAILED, RecoveryInternalError(str(exc)).failure)

    def _prepare(
        self, dropoff: PaintDropoffConfig,
        target_provider: Callable[[], NextCycleTarget | None],
        should_stop: Callable[[], bool], tool: int, user: int,
    ) -> StartRecoveryResult:
        if should_stop():
            return StartRecoveryResult(StartRecoveryOutcome.CANCELLED)
        if (not dropoff.plate_corners
                and dropoff.strategy != DropoffStrategy.PLATE_LAYOUT
                and not dropoff.alternate_drying_demo):
            return StartRecoveryResult(StartRecoveryOutcome.NOT_REQUIRED)
        corners, error = validate_plate_corners(dropoff.plate_corners)
        if error:
            raise InvalidTrayGeometryError(error)
        if dropoff.plate_robot_tool != tool or dropoff.plate_robot_user != user:
            raise TrayFrameMismatchError()
        request = StartRecoveryRequest(
            self._fresh_pose(), tuple(tuple(c) for c in corners), dropoff, target_provider,
        )
        strategy = next((s for s in self._strategies if s.matches(request)), None)
        if strategy is None:
            raise NoRecoveryStrategyError()
        route = strategy.build_route(request)
        if should_stop():
            return StartRecoveryResult(StartRecoveryOutcome.CANCELLED)
        if not route:
            return StartRecoveryResult(StartRecoveryOutcome.NOT_REQUIRED)
        _logger.info(
            "[START_RECOVERY] strategy=%s pose=%s segments=%d",
            type(strategy).__name__, request.pose, len(route),
        )
        try:
            completed = self._execute_route("Tray start recovery return", route)
        except Exception as exc:
            if should_stop():
                return StartRecoveryResult(StartRecoveryOutcome.CANCELLED)
            raise RecoveryMotionFailedError(str(exc)) from exc
        if should_stop():
            return StartRecoveryResult(StartRecoveryOutcome.CANCELLED)
        if not completed:
            raise RecoveryMotionFailedError()
        return StartRecoveryResult(StartRecoveryOutcome.RECOVERED)

    def _fresh_pose(self) -> tuple[float, ...]:
        try:
            pose = tuple(float(value) for value in self._read_pose())
            if len(pose) != 6 or not all(math.isfinite(value) for value in pose):
                raise ValueError("expected six finite axis values")
            return pose
        except Exception as exc:
            raise RecoveryPoseUnavailableError(str(exc)) from exc
