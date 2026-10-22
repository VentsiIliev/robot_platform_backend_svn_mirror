from src.applications.base.i_application_controller import IApplicationController
from src.applications.base.background_worker import BackgroundWorker


class DiagnosticsController(IApplicationController, BackgroundWorker):
    def __init__(self, model, view):
        BackgroundWorker.__init__(self)
        self._model, self._view = model, view
        self._busy = self._pending = self._stopped = False
        view.refresh_requested.connect(self.refresh)
        view.export_requested.connect(self.export_incident)
        view.destroyed.connect(self.stop)

    def load(self):
        self._view.set_directory(self._model.load())
        self.refresh()

    def refresh(self):
        if self._stopped:
            return
        if self._busy:
            self._pending = True
            return
        filters = self._view.filters()
        self._busy = True
        self._view.set_busy(True)
        self._run_in_thread(fn=lambda: self._model.query(filters),
                            on_done=self._on_done, on_error=self._on_error)

    def _on_done(self, result):
        if self._stopped:
            return
        self._busy = False
        self._view.set_busy(False)
        if self._pending:
            self._pending = False
            self.refresh()
        else:
            self._view.set_result(result)

    def export_incident(self, filters, destination):
        if self._stopped or self._busy:
            return
        self._busy = True
        self._view.set_busy(True)
        self._run_in_thread(fn=lambda: self._model.export_incident(filters, destination),
                            on_done=self._on_export_done, on_error=self._on_export_error)

    def _on_export_done(self, result):
        if self._stopped:
            return
        self._busy = False
        self._view.set_busy(False)
        self._view.set_export_result(result)
        if self._pending:
            self._pending = False
            self.refresh()

    def _on_export_error(self, error):
        if self._stopped:
            return
        self._busy = False
        self._view.set_busy(False)
        self._view.set_export_error(error)
        if self._pending:
            self._pending = False
            self.refresh()

    def _on_error(self, error):
        if self._stopped:
            return
        self._busy = False
        self._view.set_busy(False)
        self._view.set_error(error)
        if self._pending:
            self._pending = False
            self.refresh()

    def stop(self):
        if self._stopped:
            return
        self._stopped = True
        try:
            self._view.refresh_requested.disconnect(self.refresh)
            self._view.export_requested.disconnect(self.export_incident)
        except (RuntimeError, TypeError):
            pass
        self._stop_threads()
