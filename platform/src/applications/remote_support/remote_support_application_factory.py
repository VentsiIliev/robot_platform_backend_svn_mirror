from __future__ import annotations

from src.applications.base.i_application_controller import IApplicationController
from src.applications.base.i_application_model import IApplicationModel
from src.applications.base.i_application_view import IApplicationView
from src.applications.base.application_factory import ApplicationFactory
from src.applications.remote_support.controller.remote_support_controller import RemoteSupportController
from src.applications.remote_support.model.remote_support_model import RemoteSupportModel
from src.applications.remote_support.service.i_remote_support_service import IRemoteSupportService
from src.applications.remote_support.view.remote_support_view import RemoteSupportView


class RemoteSupportApplicationFactory(ApplicationFactory):

    def _create_model(self, service: IRemoteSupportService) -> IApplicationModel:
        return RemoteSupportModel(service)

    def _create_view(self) -> IApplicationView:
        return RemoteSupportView()

    def _create_controller(self, model: IApplicationModel, view: IApplicationView) -> IApplicationController:
        return RemoteSupportController(model, view)
