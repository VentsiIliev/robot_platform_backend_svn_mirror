"""Backend adapter: configuration application without exposing ROS to the domain."""
from copy import deepcopy
import logging
import math
import time

from .domain import LIVE_MONITOR_FIELDS, canonical_calibration, tool_snapshot
from .ports import ApplicationFailure

logger = logging.getLogger(__name__)
# TODO - WHAT IS THE PURPOSE OF CALIBRATION_KEYS? IS IT TO ENSURE THAT ONLY CERTAIN KEYS ARE COPIED FROM THE CONFIGURATION? IF SO, SHOULD WE DOCUMENT THIS? OR MAYBE EVEN THINK ABOUT BETTER SOLUTION BECAUSE I NOTICED THE PATTERN IN ANOTHER PARTS OF THE CODEBASE WHERE. AND I THINK IT IS CODE SMELL OR EVEN BAD ARCHITECTURE!
CALIBRATION_KEYS = ('TOOL_DEFINITIONS', 'TOOL_REGISTRY', 'TOOL_ID_MAP', 'REFERENCE_TOOL_ID',
                    'TOOL_COLLISION_PROFILE_MAP', 'WORKOBJECT_REGISTRY', 'WORKOBJECT_ID_MAP',
                    'DEFAULT_WORKOBJECT_ID', 'DEFAULT_WORKOBJECT')


def calibration_from_runtime(config):
    return {key: deepcopy(config._CONFIG[key]) for key in CALIBRATION_KEYS if key in config._CONFIG}


class LocalConfigurationRuntime:
    def __init__(self, config, node_getter, robot_getter, *, sensorless_startup=None,
                 monitor_getter=None, monitor_apply=None):
        self.config = config
        self.node_getter = node_getter
        self.robot_getter = robot_getter
        self.sensorless_startup = deepcopy(sensorless_startup)
        self.monitor_getter = monitor_getter
        self.monitor_apply = monitor_apply

    def snapshot(self, section):
        if section == 'cell_scene':
            node = self.node_getter()
            manager = getattr(node, 'cell_scene_manager', None) if node is not None else None
            return manager.snapshot() if manager is not None else None
        if section == 'calibration':
            if self.node_getter() is None or self.robot_getter() is None:
                return None
            value = calibration_from_runtime(self.config)
            if 'TOOL_DEFINITIONS' in value:
                value.pop('TOOL_REGISTRY', None)
                value.pop('TOOL_COLLISION_PROFILE_MAP', None)
            return canonical_calibration(value)
        if self.sensorless_startup is None:
            return None
        current = deepcopy(self.sensorless_startup)
        # A cached startup document is not evidence that the controller has applied monitor settings.
        monitor = self.monitor_getter() if self.monitor_getter else None
        if monitor is None:
            return None
        controller = monitor.get('_controller')
        if not isinstance(controller, dict):
            return None
        current['controller'] = deepcopy(controller)
        for key in current['monitor']:
            if key in monitor:
                current['monitor'][key] = deepcopy(monitor[key])
        return current

    def apply(self, section, document):
        if section == 'sensorless_collision':
            if self.monitor_apply is None:
                return ApplicationFailure('configuration_runtime_unavailable', 'Saved; runtime application is unavailable', retryable=True)
            patch = {key: document['monitor'][key] for key in LIVE_MONITOR_FIELDS}
            try:
                return self.monitor_apply(patch)
            except Exception as error:
                logger.exception('Saved sensorless configuration could not be applied')
                return ApplicationFailure.from_exception(error, prefix='Saved; collision controller could not confirm application')
        node = self.node_getter()
        robot = self.robot_getter()
        if node is None or robot is None:
            return ApplicationFailure('configuration_runtime_unavailable', 'Saved; robot runtime is unavailable', retryable=True)
        lock = getattr(node, 'execution_lock', None)
        if lock is None or not lock.acquire(blocking=False):
            return ApplicationFailure('configuration_robot_busy', 'Saved; robot is busy. Apply when stationary', retryable=True)
        try:
            if (bool(getattr(node, 'is_executing', False))
                    or node.is_motion_active() or node.has_pending_motion()):
                return ApplicationFailure('configuration_robot_busy', 'Saved; robot is executing. Apply when stationary', retryable=True)
            servo = getattr(robot, 'cartesian_servo', None)
            if servo is not None and str(servo.get_status().state.value) == 'running':
                return ApplicationFailure('configuration_servo_running', 'Saved; Cartesian Servo is running. Apply when stationary', retryable=True)
            measured = node.state_store.get_braking_state()
            if measured is None or not 0 <= time.monotonic() - measured.received_at <= 0.25:
                return ApplicationFailure('configuration_state_stale', 'Saved; fresh joint velocity state is unavailable', retryable=True)
            if tuple(measured.names) != tuple(getattr(self.config, 'JOINT_NAMES', ())):
                return ApplicationFailure('configuration_joint_order_mismatch', 'Saved; joint velocity order does not match this profile', retryable=False)
            values = list(measured.velocity)
            if len(values) != len(getattr(self.config, 'JOINT_NAMES', ())):
                return ApplicationFailure('configuration_joint_state_incomplete', 'Saved; joint velocity state is incomplete', retryable=False)
            if any(not math.isfinite(float(v)) or abs(float(v)) > 0.01 for v in values):
                return ApplicationFailure('configuration_robot_moving', 'Saved; robot must be stationary before applying calibration', retryable=True)
            if section == 'cell_scene':
                manager = getattr(node, 'cell_scene_manager', None)
                if manager is None:
                    return ApplicationFailure('cell_scene_unavailable', 'Saved; cell scene is unavailable', retryable=True)
                manager.apply(document)
                self.config.CELL_COLLISION_OBJECTS = deepcopy(document['CELL_COLLISION_OBJECTS'])
                self.config._CONFIG['CELL_COLLISION_OBJECTS'] = deepcopy(document['CELL_COLLISION_OBJECTS'])
            else:
                self._apply_calibration(node, robot, document)
            return None
        except Exception as error:
            logger.exception('Saved calibration could not be fully applied')
            return ApplicationFailure.from_exception(error, prefix='Saved; configuration application failed. Reload before moving')
        finally:
            lock.release()

    def _apply_calibration(self, node, robot, document):
        from utils.work_object import WorkObject
        config = self.config
        canonical = canonical_calibration(document)
        tools = tool_snapshot(canonical)
        values = {**canonical, 'TOOL_REGISTRY': tools['tool_registry'],
                  'TOOL_COLLISION_PROFILE_MAP': tools['tool_collision_profile_map']}
        active_name = getattr(node, 'active_tool_name', 'TOOL_0')
        old_ids = dict(config.TOOL_ID_MAP)
        active_id = next((key for key, value in old_ids.items() if value == active_name), None)
        old = calibration_from_runtime(config)
        old_workobjects = deepcopy(robot.workobject_registry)
        old_active_id = robot.get_active_workobject()['user_id']

        def install(data):
            for key in CALIBRATION_KEYS:
                if key not in data:
                    config._CONFIG.pop(key, None)
                    if hasattr(config, key):
                        delattr(config, key)
                    continue
                current = getattr(config, key, None)
                value = deepcopy(data[key])
                if isinstance(current, dict) and isinstance(value, dict):
                    current.clear()
                    current.update(value)
                    value = current
                setattr(config, key, value)
                config._CONFIG[key] = value
        try:
            install(values)
            new_active = config.TOOL_ID_MAP.get(active_id, active_name)
            if new_active in config.TOOL_REGISTRY:
                node.set_tool(new_active)
            for user_id, object_name in config.WORKOBJECT_ID_MAP.items():
                robot.set_workobject(WorkObject(*config.WORKOBJECT_REGISTRY[object_name]), user_id=int(user_id))
            active = robot.get_active_workobject()
            robot.set_active_workobject(int(active.get('user_id', 0)))
        except Exception:
            install(old)
            # Restore both derived TCP state and work-object transforms if any adapter failed midway.
            node.set_tool(active_name)
            robot.workobject_registry.clear()
            robot.workobject_registry.update(old_workobjects)
            robot.set_active_workobject(old_active_id)
            raise
