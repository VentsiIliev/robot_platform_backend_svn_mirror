from src.applications.base.i_application_model import IApplicationModel
from src.applications.contour_dxf.service.i_contour_dxf_service import IContourDXFService

class ContourDXFModel(IApplicationModel):
    def __init__(self, service: IContourDXFService):
        self._service = service
    def load(self):
        return self._service.get_info()
    def start(self):
        self._service.start()
    def stop(self):
        self._service.stop()
    def live_frame(self):
        return self._service.get_live_frame()
    def capture(self, smooth):
        return self._service.capture(smooth)
    def captured(self):
        return self._service.get_capture()
    def calibrate(self, width, height, tolerance):
        self._service.calibrate(width, height, tolerance)
    def save(self, destination):
        self._service.export(destination)
