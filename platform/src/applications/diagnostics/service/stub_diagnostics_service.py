from .i_diagnostics_service import IDiagnosticsService


class StubDiagnosticsService(IDiagnosticsService):
    def export_incident(self, filters: dict, destination: str) -> dict:
        raise RuntimeError('Sample data service does not write exports')

    def initial_directory(self) -> str:
        return '/sample/diagnostics'

    def query(self, filters: dict) -> dict:
        return {'events': [{
            'timestamp': '2026-10-21T08:00:00+00:00', 'level': 'INFO',
            'event': 'settings.collision.edited', 'message': 'settings.collision.edited',
            '_display_time': '2026-10-21T11:00:00.000+03:00',
            '_summary': 'active_stop_enabled · True → False',
            'fields': {'field': 'active_stop_enabled', 'before': True, 'after': False,
                       'persisted': False, 'applied': False},
            'context': {'action_id': 'sample-action', 'actor': {'user_id': '42'}},
        }], 'warnings': [], 'matched': 1, 'limited': False}
