from src.applications.base.i_application_model import IApplicationModel
from ..service.i_image_capture_service import CapturedImage, IImageCaptureService


class ImageCaptureModel(IApplicationModel):
    def __init__(self, service: IImageCaptureService):
        self._service = service
        self.image = None
        self.saved_path = ""

    def load(self) -> str:
        return self._service.output_directory()

    def capture(self) -> CapturedImage:
        self.image = None
        self.saved_path = ""
        self.image = self._service.capture()
        return self.image

    def save(self) -> None:
        if self.image is None:
            raise ValueError("Capture an image before saving.")
        self.saved_path = self._service.save_image(self.image)
