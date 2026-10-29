"""Run-local checks before cycles; completed painting advances the schedule."""

from src.robot_systems.paint.contracts.paint_head_check.errors import PaintHeadContractError
from src.robot_systems.paint.contracts.paint_head_check.interfaces import IPaintHeadCheckPolicy
from src.robot_systems.paint.contracts.paint_head_check.models import (
    HeadCheckProgress,
    HeadCheckScheduleDecision,
)


class PaintHeadCheckSession:
    """One accepted Start owns one instance; Resume reuses the current checkpoint."""

    def __init__(self, policy: IPaintHeadCheckPolicy) -> None:
        self._policy = policy
        self._completed_workpieces = 0
        self._checked_before_workpiece: int | None = None

    @property
    def progress(self) -> HeadCheckProgress:
        return HeadCheckProgress(self._completed_workpieces)

    def check_before_cycle_due(self) -> bool:
        return (
            self._checked_before_workpiece != self._completed_workpieces
            and self._policy.evaluate(self.progress) is HeadCheckScheduleDecision.DUE
        )

    def record_completed_cycle(self) -> None:
        if self.check_before_cycle_due():
            raise PaintHeadContractError(
                "A paint cycle cannot complete before its required head check"
            )
        self._completed_workpieces += 1

    def mark_check_complete(self) -> None:
        """Reporting/acceptance satisfies this checkpoint; rejection does not."""
        self._checked_before_workpiece = self._completed_workpieces
