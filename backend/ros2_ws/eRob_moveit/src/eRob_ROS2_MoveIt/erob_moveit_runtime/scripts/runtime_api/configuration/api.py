from __future__ import annotations
import logging
from typing import Any
from runtime_api.contracts import ApiResponse, api_operation
from runtime_api.common import ApiSettings
from runtime_gateway.base import RuntimeGateway
from .responses import ConfigurationResponse, RegistryResponse


logger = logging.getLogger(__name__)

class ConfigurationApi:
    """Configuration operations shared by HTTP and future gateway transports."""

    def __init__(self, gateway: RuntimeGateway, settings: ApiSettings = ApiSettings()):
        self._gateway = gateway
        self._settings = settings
        self._port = settings.port

    @api_operation("configuration.tool_registry")
    def tool_registry(self) -> ApiResponse[RegistryResponse]:
        return ApiResponse({"success": True, **self._gateway.tool_registry()})

    @api_operation("configuration.update_tool_registry")
    def update_tool_registry(self, tool_id: int, data: dict[str, Any] | None) -> ApiResponse[RegistryResponse]:
        from runtime_api.control.requests import identifier
        tool_id = identifier(tool_id, 'tool_id')
        if data is not None and 'persist' in data and type(data['persist']) is not bool:
            raise ValueError('persist must be a boolean')
        payload = data or {}
        snapshot = self._gateway.update_tool_registry(
            tool_id=tool_id,
            name=payload.get("name"),
            transform=payload.get("transform"),
            persist=bool(payload.get("persist", False)),
            collision_profile=payload.get("collision_profile"),
        )
        return ApiResponse({"success": True, **snapshot},
                           409 if snapshot.get("pending_application") else 200)

    @api_operation("configuration.workobject_registry")
    def workobject_registry(self) -> ApiResponse[RegistryResponse]:
        return ApiResponse({"success": True, **self._gateway.workobject_registry()})

    @api_operation("configuration.update_workobject_registry")
    def update_workobject_registry(self, user_id: int, data: dict[str, Any] | None) -> ApiResponse[RegistryResponse]:
        from runtime_api.control.requests import identifier
        user_id = identifier(user_id, 'user_id')
        if data is not None and 'persist' in data and type(data['persist']) is not bool:
            raise ValueError('persist must be a boolean')
        payload = data or {}
        snapshot = self._gateway.update_workobject_registry(
            user_id=user_id,
            name=payload.get("name"),
            transform=payload.get("transform") or payload.get("origin"),
            persist=bool(payload.get("persist", False)),
        )
        return ApiResponse({"success": True, **snapshot},
                           409 if snapshot.get("pending_application") else 200)

    @api_operation('configuration.catalog')
    def catalog(self) -> ApiResponse[ConfigurationResponse]:
        return ApiResponse(self._gateway.configuration_catalog())

    @api_operation('configuration.get')
    def get(self, section: str) -> ApiResponse[ConfigurationResponse]:
        from .requests import section_name
        return ApiResponse(self._gateway.get_configuration(section_name(section)))

    @api_operation('configuration.update')
    def update(self, section: str, data: dict[str, Any] | None, *,
               tool_id: int | None = None, user_id: int | None = None) -> ApiResponse[ConfigurationResponse]:
        from .requests import ConfigurationUpdateRequest, section_name
        from runtime_api.control.requests import identifier
        section = section_name(section)
        request = ConfigurationUpdateRequest.parse(data)
        if tool_id is not None:
            tool_id = identifier(tool_id, 'tool_id')
        if user_id is not None:
            user_id = identifier(user_id, 'user_id')
        if (tool_id is not None or user_id is not None) and section != 'calibration':
            raise ValueError('Tool and work-object edits require the calibration section')
        if tool_id is not None and user_id is not None:
            raise ValueError('Choose either tool_id or user_id')
        return ApiResponse(self._gateway.update_configuration(
            section, request.changes, request.expected_revision, tool_id=tool_id, user_id=user_id))

    @api_operation('configuration.apply')
    def apply(self, section: str, data: dict[str, Any] | None) -> ApiResponse[ConfigurationResponse]:
        from .requests import ConfigurationUpdateRequest, section_name
        request = ConfigurationUpdateRequest.parse(data, apply_only=True)
        return ApiResponse(self._gateway.apply_configuration(section_name(section), request.expected_revision))

    @api_operation('configuration.get_collision_monitor')
    def get_collision_monitor(self) -> ApiResponse[ConfigurationResponse]:
        return ApiResponse({'success': True, 'config': self._gateway.collision_monitor_configuration()})

    @api_operation('configuration.update_collision_monitor')
    def update_collision_monitor(self, data: dict[str, Any] | None) -> ApiResponse[ConfigurationResponse]:
        allowed = {'detection_enabled', 'active_stop_enabled', 'effort_following_error_detection_enabled',
                   'collision_sensitivity_percent', 'confirm_duration_ms', 'dynamic_threshold_enabled',
                   'dynamic_threshold_decay_sec', 'dynamic_threshold_max_ratio', 'effort_thresholds',
                   'following_error_thresholds', 'external_torque_thresholds', 'diagnostics_enabled'}
        if not data or set(data) - allowed:
            raise ValueError(f'Unsupported collision configuration fields: {sorted(set(data or {}) - allowed)}')
        result = self._gateway.update_collision_monitor_configuration(data)
        return ApiResponse({**result, 'saved_successfully': True, 'success': not result['pending_application'],
                            'config': (result['applied'] or result['saved'])['monitor']},
                           409 if result['pending_application'] else 200)
