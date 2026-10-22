from src.applications.base.application_interface import IApplication
from .diagnostics_application_factory import DiagnosticsApplicationFactory
from .service.i_diagnostics_service import IDiagnosticsService


class DiagnosticsApplication(IApplication):
    def __init__(self, service: IDiagnosticsService):
        self._service = service

    def register(self, messaging_service):
        pass

    def create_widget(self):
        return DiagnosticsApplicationFactory().build(self._service)
