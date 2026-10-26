from src.applications.base.widget_application import WidgetApplication
from .image_capture_application_factory import ImageCaptureApplicationFactory
from .service.i_image_capture_service import IImageCaptureService


class ImageCaptureApplication(WidgetApplication):
    def __init__(self, service: IImageCaptureService):
        super().__init__(widget_factory=lambda _ms: ImageCaptureApplicationFactory().build(service))
