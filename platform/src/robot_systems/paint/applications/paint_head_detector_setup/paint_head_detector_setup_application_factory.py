"""Standard platform application factory; ownership and cleanup belong to its base."""

from src.applications.base.application_factory import ApplicationFactory

from .controller.paint_head_detector_setup_controller import PaintHeadDetectorSetupController
from .model.paint_head_detector_setup_model import PaintHeadDetectorSetupModel
from .service.i_paint_head_detector_setup_service import IPaintHeadDetectorSetupService
from .view.paint_head_detector_setup_view import PaintHeadDetectorSetupView


class PaintHeadDetectorSetupApplicationFactory(ApplicationFactory):
    def _create_model(self, service: IPaintHeadDetectorSetupService) -> PaintHeadDetectorSetupModel:
        return PaintHeadDetectorSetupModel(service)

    def _create_view(self) -> PaintHeadDetectorSetupView:
        return PaintHeadDetectorSetupView()

    def _create_controller(
        self,
        model: PaintHeadDetectorSetupModel,
        view: PaintHeadDetectorSetupView,
    ) -> PaintHeadDetectorSetupController:
        return PaintHeadDetectorSetupController(model, view)
