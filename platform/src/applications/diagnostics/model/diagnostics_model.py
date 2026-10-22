from src.applications.base.i_application_model import IApplicationModel
from ..service.i_diagnostics_service import IDiagnosticsService


class DiagnosticsModel(IApplicationModel):
    def __init__(self, service: IDiagnosticsService):
        self._service = service

    def load(self):
        return self._service.initial_directory()

    def query(self, filters: dict) -> dict:
        return self._service.query(filters)

    def save(self, *args, **kwargs) -> None:
        raise PermissionError('Diagnostics history is read-only')

    def export_incident(self, filters: dict, destination: str) -> dict:
        return self._service.export_incident(filters, destination)
