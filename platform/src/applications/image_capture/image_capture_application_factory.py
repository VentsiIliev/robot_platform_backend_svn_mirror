from __future__ import annotations

from src.applications.base.i_application_controller import IApplicationController
from src.applications.base.i_application_model import IApplicationModel
from src.applications.base.i_application_view import IApplicationView
from src.applications.base.application_factory import ApplicationFactory
from src.applications.image_capture.controller.image_capture_controller import ImageCaptureController
from src.applications.image_capture.model.image_capture_model import ImageCaptureModel
from src.applications.image_capture.service.i_image_capture_service import IImageCaptureService
from src.applications.image_capture.view.image_capture_view import ImageCaptureView


class ImageCaptureApplicationFactory(ApplicationFactory):

    def _create_model(self, service: IImageCaptureService) -> IApplicationModel:
        return ImageCaptureModel(service)

    def _create_view(self) -> IApplicationView:
        return ImageCaptureView()

    def _create_controller(self, model: IApplicationModel, view: IApplicationView) -> IApplicationController:
        return ImageCaptureController(model, view)
