"""Lazy application adapter accepting only its application service contract."""

from PyQt6.QtWidgets import QWidget

from src.applications.base.widget_application import WidgetApplication

from .service.i_paint_head_detector_setup_service import IPaintHeadDetectorSetupService


class PaintHeadDetectorSetupApplication(WidgetApplication):
    def __init__(self, service: IPaintHeadDetectorSetupService) -> None:
        self._service = service
        super().__init__(self._build_widget)

    def _build_widget(self, _messaging: object) -> QWidget:
        from .paint_head_detector_setup_application_factory import (
            PaintHeadDetectorSetupApplicationFactory,
        )

        return PaintHeadDetectorSetupApplicationFactory().build(self._service)
