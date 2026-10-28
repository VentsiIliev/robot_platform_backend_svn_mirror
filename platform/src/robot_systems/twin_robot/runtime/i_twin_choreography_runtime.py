from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from typing import Any

from .activity import TwinRuntimeActivity


class ITwinChoreographyRuntime(ABC):
    """Transport-neutral runtime contract used by TwinRobotSystem.

    The platform owns choreography authoring/orchestration. The concrete robot
    stack owns planning, timing synchronization and controller execution.
    """

    @abstractmethod
    def robot(self, robot_name: str) -> Any:
        """Return the robot-scoped gateway used for jog/state operations."""
        ...

    @abstractmethod
    def prepare_choreography(self, choreography) -> Any:
        """Plan both robots without executing either trajectory.

        The result must expose ``robot1_ready`` and ``robot2_ready`` (attributes
        or dict keys) and retain the two prepared trajectories plus their exact
        start-joint anchors.
        """
        ...

    @abstractmethod
    def execute_prepared(self, prepared, loop_count: int = 1):
        """Execute an already prepared pair only after both sides are ready.

        Implementations are responsible for moving both robots to the exact
        saved start-joint anchors, verifying the branch anchors, releasing both
        controller goals through the synchronization barrier, and reusing the
        same prepared pair for subsequent loops.
        """
        ...

    @abstractmethod
    def stop(self):
        """Request controlled stop of both robots."""
        ...

    @abstractmethod
    def get_activity(self) -> TwinRuntimeActivity:
        """Return authoritative combined activity, including jog and queued starts.

        IDLE means both robots have no running/paused/stopping/pending execution.
        A stale/disconnected/unverifiable state is UNKNOWN or an exception.
        A successful start/stop response alone is not evidence of idle activity.
        """
        ...

    @abstractmethod
    def hold_idle(self) -> AbstractContextManager[bool]:
        """Atomically reserve idle execution until the context exits.

        Yield True only if both robots are idle and no execution (including jog
        or external starts) can start until release. Yield False when busy;
        raise when readiness cannot be established. Never stop either robot.
        get_activity() must remain callable while the caller holds this lease.
        """
        ...
