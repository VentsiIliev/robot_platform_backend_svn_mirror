"""Reusable shell wiring for every robot system."""

from src.applications.base.widget_application import WidgetApplication
from .network_settings_factory import NetworkSettingsFactory
from .service.network_settings_service import NetworkSettingsService


def build_network_settings_application(_robot_system, *, show_remote_support: bool = True):
    service = NetworkSettingsService()
    factory = NetworkSettingsFactory(show_remote_support=show_remote_support)
    return WidgetApplication(widget_factory=lambda _messaging: factory.build(service))
