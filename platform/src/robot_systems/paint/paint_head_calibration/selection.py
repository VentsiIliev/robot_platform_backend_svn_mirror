"""Reserve the existing process manager while publishing a runtime selection."""

from collections.abc import Iterator
from contextlib import contextmanager
from uuid import uuid4

from src.engine.system.i_system_manager import ISystemManager
from src.robot_systems.paint.component_ids import ProcessID


class CalibrationSelectionReservation:
    def __init__(self, manager: ISystemManager) -> None:
        self._manager = manager

    @contextmanager
    def hold(self) -> Iterator[bool]:
        # A unique owner prevents another selection from reentering SystemManager's
        # same-owner fast path and releasing this transaction's reservation.
        owner = f"{ProcessID.HEAD_CALIBRATION_SELECTION.value}:{uuid4().hex}"
        acquired = self._manager.acquire(owner)
        try:
            yield acquired
        finally:
            if acquired:
                self._manager.release(owner)
