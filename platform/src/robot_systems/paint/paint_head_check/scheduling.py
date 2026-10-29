"""Pure scheduling strategies; session progress is supplied by their caller."""

from src.robot_systems.paint.contracts.paint_head_check.errors import PaintHeadConfigurationError
from src.robot_systems.paint.contracts.paint_head_check.interfaces import IPaintHeadCheckPolicy
from src.robot_systems.paint.contracts.paint_head_check.models import (
    HeadCheckProgress,
    HeadCheckScheduleDecision,
)


class EveryCycleHeadCheckPolicy(IPaintHeadCheckPolicy):
    def evaluate(self, progress: HeadCheckProgress) -> HeadCheckScheduleDecision:
        return HeadCheckScheduleDecision.DUE


class DisabledHeadCheckPolicy(IPaintHeadCheckPolicy):
    def evaluate(self, progress: HeadCheckProgress) -> HeadCheckScheduleDecision:
        return HeadCheckScheduleDecision.NOT_DUE


class FirstCycleHeadCheckPolicy(IPaintHeadCheckPolicy):
    def evaluate(self, progress: HeadCheckProgress) -> HeadCheckScheduleDecision:
        return (
            HeadCheckScheduleDecision.DUE
            if progress.completed_workpieces == 0
            else HeadCheckScheduleDecision.NOT_DUE
        )


class FirstThenIntervalHeadCheckPolicy(IPaintHeadCheckPolicy):
    def __init__(self, interval_cycles: int) -> None:
        if type(interval_cycles) is not int or interval_cycles < 1:
            raise PaintHeadConfigurationError("Check interval must be a positive integer")
        self._interval_cycles = interval_cycles

    def evaluate(self, progress: HeadCheckProgress) -> HeadCheckScheduleDecision:
        return (
            HeadCheckScheduleDecision.DUE
            if progress.completed_workpieces % self._interval_cycles == 0
            else HeadCheckScheduleDecision.NOT_DUE
        )
