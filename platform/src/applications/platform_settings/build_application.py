"""Reusable Platform Settings wiring for every robot system."""

from src.applications.base.widget_application import WidgetApplication
from .platform_settings_factory import PlatformSettingsFactory
from .service.platform_settings_service import PlatformSettingsService


def build_platform_settings_application(_robot_system):
    service = PlatformSettingsService()
    return WidgetApplication(
        widget_factory=lambda _messaging: PlatformSettingsFactory().build(service)
    )
