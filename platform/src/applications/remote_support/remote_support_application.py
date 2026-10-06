from src.applications.base.widget_application import WidgetApplication
from .remote_support_application_factory import RemoteSupportApplicationFactory
from .service.i_remote_support_service import IRemoteSupportService


class RemoteSupportApplication(WidgetApplication):
    def __init__(self, service: IRemoteSupportService):
        factory = RemoteSupportApplicationFactory()
        super().__init__(widget_factory=lambda _ms: factory.build(service))
