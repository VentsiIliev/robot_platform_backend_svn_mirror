from __future__ import annotations

from src.applications.base.i_application_controller import IApplicationController
from src.applications.base.i_application_model import IApplicationModel
from src.applications.base.i_application_view import IApplicationView
from src.applications.base.application_factory import ApplicationFactory
from src.applications.contour_dxf.controller.contour_dxf_controller import ContourDXFController
from src.applications.contour_dxf.model.contour_dxf_model import ContourDXFModel
from src.applications.contour_dxf.service.i_contour_dxf_service import IContourDXFService
from src.applications.contour_dxf.view.contour_dxf_view import ContourDXFView


class ContourDXFFactory(ApplicationFactory):

    def _create_model(self, service: IContourDXFService) -> IApplicationModel:
        return ContourDXFModel(service)

    def _create_view(self) -> IApplicationView:
        return ContourDXFView()

    def _create_controller(self, model: IApplicationModel, view: IApplicationView) -> IApplicationController:
        return ContourDXFController(model, view)
