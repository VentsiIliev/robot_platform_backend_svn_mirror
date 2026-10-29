"""Reporting adapters keep logging and dashboard effects outside policies."""

import logging

from src.robot_systems.paint.contracts.paint_head_check.errors import HeadInspectionFailure
from src.robot_systems.paint.contracts.paint_head_check.interfaces import IPaintHeadCheckObserver
from src.robot_systems.paint.contracts.paint_head_check.models import (
    HeadCheckContext,
    PaintHeadObservation,
)


class LoggingPaintHeadCheckObserver(IPaintHeadCheckObserver):
    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def inspection_started(self, context: HeadCheckContext) -> None:
        self._logger.info(
            "Paint-head check starting before cycle=%d",
            context.progress.completed_workpieces + 1,
        )

    def observation_received(
        self,
        observation: PaintHeadObservation,
        context: HeadCheckContext,
    ) -> None:
        self._logger.info(
            "Paint-head check state=%s observed=%s reason=%s completed_workpieces=%d "
            "attempt=%d frame=%d calibration_revision=%d alignment=%s",
            observation.state.name,
            observation.observed_state.name,
            observation.reason.name,
            context.progress.completed_workpieces,
            context.attempt_number,
            observation.frame_sequence,
            observation.calibration_revision,
            observation.alignment,
        )

    def inspection_failed(
        self,
        failure: HeadInspectionFailure,
        context: HeadCheckContext,
    ) -> None:
        self._logger.warning(
            "Paint-head check failure=%s completed_workpieces=%d attempt=%d: %s",
            failure.code.name,
            context.progress.completed_workpieces,
            context.attempt_number,
            failure.message,
        )


class CompositePaintHeadCheckObserver(IPaintHeadCheckObserver):
    def __init__(self, observers: tuple[IPaintHeadCheckObserver, ...]) -> None:
        self._observers = observers

    def inspection_started(self, context: HeadCheckContext) -> None:
        for observer in self._observers:
            observer.inspection_started(context)

    def observation_received(
        self, observation: PaintHeadObservation, context: HeadCheckContext
    ) -> None:
        for observer in self._observers:
            observer.observation_received(observation, context)

    def inspection_failed(self, failure: HeadInspectionFailure, context: HeadCheckContext) -> None:
        for observer in self._observers:
            observer.inspection_failed(failure, context)
