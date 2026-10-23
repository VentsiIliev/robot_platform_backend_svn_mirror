"""Composition root for the backend-owned profile configuration service."""
from pathlib import Path

from .domain import Unavailable
from .repository import YamlProfileRepository
from .runtime import LocalConfigurationRuntime
from .service import ConfigurationService


def build_configuration_service(config, node_getter=lambda: None, robot_getter=lambda: None):
    calibration = config._CONFIG.get('_CALIBRATION_CONFIG_PATH')
    profile = config._CONFIG.get('ACTIVE_PROFILE')
    if not calibration or not profile:
        raise Unavailable('This backend does not define a profile-owned calibration store')
    root = Path(config._CONFIG['_ACTIVE_RUNTIME_CONFIG_PATH']).resolve().parent
    paths = {'calibration': calibration}
    sensorless = config._CONFIG.get('SENSORLESS_COLLISION_CONFIG_PATH')
    if sensorless:
        paths['sensorless_collision'] = sensorless
    cell_path = config._CONFIG.get('CELL_SCENE_PATH')
    if cell_path:
        paths['cell_scene'] = root / cell_path
    repository = YamlProfileRepository(profile, paths, root=root)
    startup = config._CONFIG.get('_SENSORLESS_COLLISION_STARTUP')
    runtime = LocalConfigurationRuntime(config, node_getter, robot_getter, sensorless_startup=startup)
    return ConfigurationService(repository, runtime, collision_profiles=config._CONFIG.get('TOOL_COLLISION_PROFILES', {}))
