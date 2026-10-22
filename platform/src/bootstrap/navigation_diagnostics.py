"""Qt shell adapter; the shared shell imports no engine diagnostics."""
class NavigationDiagnostics:
    def __init__(self, shell, actions):
        self._shell = shell
        self._actions = actions
        self._pending = {}

    def start(self):
        self._shell.navigation_event.connect(self._on_navigation)

    def stop(self):
        try:
            self._shell.navigation_event.disconnect(self._on_navigation)
        except (TypeError, RuntimeError):
            pass
        self._pending.clear()

    def _on_navigation(self, event):
        try:
            payload = dict(event)
            outcome = payload.pop('outcome')
            name = payload.pop('event')
            key = payload.pop('request_id')
            if outcome == 'started':
                token = self._actions.context()
                # Normally paired synchronously; bound abandoned starts too.
                if len(self._pending) >= 64:
                    self._pending.pop(next(iter(self._pending)))
                self._pending[key] = token
            else:
                token = self._pending.pop(key, None)
            self._actions.record(name, context=token, outcome=outcome, **payload)
        except Exception:
            pass
