from src.engine.core.i_messaging_service import IMessagingService
from src.engine.core.messaging_service import MessagingService
from src.engine.diagnostics.i_diagnostics_service import IDiagnosticsService
from src.engine.diagnostics.service import NullDiagnosticsService


class EngineContext:
    def __init__(self, diagnostics_service: IDiagnosticsService | None = None):
        self.messaging_service: IMessagingService = MessagingService()   # concrete here only
        self.diagnostics_service: IDiagnosticsService = (
            NullDiagnosticsService() if diagnostics_service is None else diagnostics_service)

    @classmethod
    def build(cls, diagnostics_service: IDiagnosticsService | None = None) -> 'EngineContext':
        return cls(diagnostics_service)
