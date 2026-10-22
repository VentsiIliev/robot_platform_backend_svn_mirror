from __future__ import annotations

from src.applications.base.i_application_controller import IApplicationController
from src.applications.base.i_application_model import IApplicationModel
from src.applications.base.i_application_view import IApplicationView
from src.applications.base.application_factory import ApplicationFactory
from src.applications.diagnostics.controller.diagnostics_controller import DiagnosticsController
from src.applications.diagnostics.model.diagnostics_model import DiagnosticsModel
from src.applications.diagnostics.service.i_diagnostics_service import IDiagnosticsService
from src.applications.diagnostics.view.diagnostics_view import DiagnosticsView


class DiagnosticsApplicationFactory(ApplicationFactory):

    def _create_model(self, service: IDiagnosticsService) -> IApplicationModel:
        return DiagnosticsModel(service)

    def _create_view(self) -> IApplicationView:
        return DiagnosticsView()

    def _create_controller(self, model: IApplicationModel, view: IApplicationView) -> IApplicationController:
        return DiagnosticsController(model, view)
