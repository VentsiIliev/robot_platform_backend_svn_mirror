from functools import partial
from src.applications.base.i_application_controller import IApplicationController
from src.applications.base.background_worker import BackgroundWorker

class ContourDXFController(IApplicationController, BackgroundWorker):
    def __init__(self, model, view):
        BackgroundWorker.__init__(self)
        self._model, self._view = model, view
        self._active = True
        self._busy = False
        self._frame_busy = False
        self._connected = False
        self._preview_error = False
        view.camera_requested.connect(self._on_camera)
        view.capture_requested.connect(self._on_capture)
        view.calibrate_requested.connect(self._on_calibrate)
        view.export_requested.connect(self._on_export)
        view.refresh_requested.connect(self._on_refresh)

    def load(self):
        self._show_info()
        self._on_camera()

    def has_active_operations(self):
        return self._busy

    def _run(self, fn, done, status):
        if self._busy or not self._active:
            return
        self._busy = True
        self._view.set_busy(True)
        self._view.set_status(status)
        self._run_in_thread(fn, done, self._on_error)

    def _finish(self, status):
        if not self._active:
            return
        self._busy = False
        self._view.set_busy(False)
        self._show_info()
        self._view.set_status(status)

    def _show_info(self):
        info = self._model.load()
        self._view.set_info(info.source, info.mm_per_pixel, info.correction, info.output_dir,
                            info.calibration_path, info.residual_mm, info.last_export)

    def _on_camera(self):
        if self._busy:
            return
        if self._connected:
            self._view.stop_refresh()
            self._connected = False
            self._run(self._model.stop, self._on_stopped, 'disconnecting')
        else:
            self._run(self._model.start, self._on_started, 'connecting')

    def _on_started(self, _result):
        if not self._active:
            return
        self._connected = True
        self._view.set_connected(True)
        self._view.start_refresh()
        self._finish('ready')
        self._on_refresh()

    def _on_stopped(self, _result):
        if self._active:
            self._view.set_connected(False)
            self._finish('disconnected')

    def _on_refresh(self):
        if self._connected and self._active and not self._frame_busy:
            self._frame_busy = True
            self._run_in_thread(self._model.live_frame, self._on_frame, self._on_frame_error)

    def _on_frame(self, frame):
        self._frame_busy = False
        if self._active and self._connected and frame is not None:
            self._view.set_live_frame(frame.width, frame.height, frame.rgb)
            if self._preview_error and not self._busy:
                self._view.set_status('ready')
            self._preview_error = False

    def _on_frame_error(self, error):
        self._frame_busy = False
        if self._active and self._connected and not self._busy:
            self._preview_error = True
            self._view.set_status('error', error)

    def _on_capture(self, smooth):
        self._run(partial(self._model.capture, smooth), self._on_captured, 'capturing')

    def _show_capture(self, result):
        frame = result.preview
        self._view.set_capture(frame.width, frame.height, frame.rgb, result.width_mm,
                               result.height_mm, result.point_count, result.exportable)

    def _on_captured(self, result):
        if self._active:
            self._show_capture(result)
            self._finish('captured')

    def _on_calibrate(self, width, height, tolerance):
        self._run(partial(self._model.calibrate, width, height, tolerance), self._on_calibrated, 'calibrating')

    def _on_calibrated(self, _result):
        if self._active:
            self._show_capture(self._model.captured())
            self._finish('calibrated')

    def _on_export(self, destination):
        self._run(partial(self._model.save, destination), self._on_exported, 'exporting')

    def _on_exported(self, _result):
        self._finish('exported')

    def _on_error(self, message):
        if self._active:
            self._busy = False
            self._view.set_busy(False)
            self._view.set_connected(self._connected)
            self._view.set_status('error', message)
            result = self._model.captured()
            if result is not None:
                self._show_capture(result)

    def stop(self):
        if not self._active:
            return
        self._active = False
        self._view.stop_refresh()
        self._stop_threads()
        self._run_in_thread(self._model.stop, self._on_shutdown, self._on_shutdown_error)
        self._stop_threads()

    def _on_shutdown(self, _result):
        pass

    def _on_shutdown_error(self, message):
        self._logger.error('Camera shutdown failed: %s', message)
