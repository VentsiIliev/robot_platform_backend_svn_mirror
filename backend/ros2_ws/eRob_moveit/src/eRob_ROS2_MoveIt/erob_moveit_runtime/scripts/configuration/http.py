"""Compatibility import for the HTTP adapter. Pass ConfigurationApi, never a service."""
from rest.routes.configuration import configuration_blueprint

__all__ = ['configuration_blueprint']
