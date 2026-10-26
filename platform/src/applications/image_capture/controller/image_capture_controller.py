import json

from src.applications.base.background_worker import BackgroundWorker
from src.applications.base.i_application_controller import IApplicationController


class ImageCaptureController(IApplicationController, BackgroundWorker):
    def __init__(self, model, view):
        BackgroundWorker.__init__(self)
        self._model = model
        self._view = view
        self._stopped = False
        view.capture_requested.connect(self._capture)
        view.save_requested.connect(self._save)

    def load(self) -> None:
        self._view.set_directory(self._model.load())

    def stop(self) -> None:
        self._stopped = True
        self._stop_threads()

    def _capture(self) -> None:
        if self._stopped or self.has_running_workers():
            return
        self._view.set_image(None)
        self._view.set_decomposition(None)
        self._view.set_robot_image(None)
        self._view.set_sampled_image(None)
        self._view.set_status("Capturing…")
        self._view.set_busy(True)
        self._run_in_thread(self._model.capture, self._captured, self._failed)

    def _captured(self, image) -> None:
        if not self._stopped:
            self._view.set_image(image.preview)
            self._view.set_decomposition(
                image.decomposition_preview, image.line_count, image.arc_count,
                image.exceeds_tolerance, image.failed_contours,
            )
            self._view.set_status("Detected contours: {detail}", str(len(image.contours)))
            robot_counts = None
            if image.robot_result is not None:
                entries = json.loads(image.robot_result)["contours"]
                primitives = [p for e in entries for p in e["primitives"]]
                robot_counts = (sum(p["type"] == "line" for p in primitives),
                                sum(p["type"] == "arc" for p in primitives),
                                sum(not p["within_tol"] for p in primitives),
                                sum(e["status"] != "ok" for e in entries))
            self._view.set_robot_image(image.robot_preview, robot_counts)
            self._view.set_sampled_image(image.sampled_preview)

    def _save(self) -> None:
        if self._stopped or self.has_running_workers():
            return
        self._view.set_status("Saving…")
        self._view.set_busy(True)
        self._run_in_thread(self._model.save, self._saved, self._failed)

    def _saved(self, _result) -> None:
        if not self._stopped:
            self._view.set_status("Saved: {detail}", self._model.saved_path)

    def _failed(self, message) -> None:
        self._logger.error("Image capture operation failed: %s", message)
        if not self._stopped:
            self._view.set_status("Operation failed: {detail}", message)

    def _on_thread_finished(self) -> None:
        super()._on_thread_finished()
        if not self._stopped:
            self._view.set_busy(self.has_running_workers())
