from src.applications.base.widget_application import WidgetApplication
from .contour_dxf_factory import ContourDXFFactory
from .service.i_contour_dxf_service import IContourDXFService

class ContourDXFApplication(WidgetApplication):
    def __init__(self, service: IContourDXFService):
        self._service = service
        super().__init__(self._build_widget)
    def _build_widget(self, _messaging):
        return ContourDXFFactory().build(self._service)
