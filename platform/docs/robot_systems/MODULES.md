# Module reference: `src/robot_systems`

[Package guide](README.md) · [Complete source index](../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [base_robot_system.py](#base_robot_systempy)
- [default_service_builders.py](#default_service_builderspy)
- [robot_system_bootstrap_provider.py](#robot_system_bootstrap_providerpy)
- [system_builder.py](#system_builderpy)

## `__init__.py`

Source: [src/robot_systems/__init__.py](../../src/robot_systems/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `base_robot_system.py`

Source: [src/robot_systems/base_robot_system.py](../../src/robot_systems/base_robot_system.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `abc`, `enum`, `logging`, `os`, `src.engine.common_settings_ids`, `src.engine.process.service_health_registry`, `src.engine.repositories.interfaces`, `src.engine.robot.calibration.robot_calibration.metrics`, `src.engine.robot.targeting.end_effector_point`, `src.engine.robot.targeting.jog_frame_pose_resolver`, `src.engine.robot.targeting.point_registry`, `src.engine.robot.targeting.target_frame`, `src.engine.robot.targeting.vision_target_resolver`, `src.engine.updates.paths`, `src.engine.vision.homography_residual_transformer`, `src.shared_contracts.declarations`, `sys`, `typing`.

### `BaseRobotSystem`

```python
class BaseRobotSystem(ABC):
```

Subclasses declare: metadata: SystemMetadata — identity services: list[ServiceSpec] — required/optional service contracts Platform calls vision_service.start(services_dict) to resolve and inject.

Declared fields/defaults:

```python
metadata: ClassVar[SystemMetadata] = SystemMetadata(name='UnnamedSystem')
services: ClassVar[List[ServiceSpec]] = []
settings_specs: ClassVar[List[SettingsSpec]] = []
work_areas: ClassVar[List[WorkAreaDefinition]] = []
movement_groups: ClassVar[List[MovementGroupDefinition]] = []
dispense_channels: ClassVar[List[DispenseChannelDefinition]] = []
tools: ClassVar[List[ToolDefinition]] = []
tool_slots: ClassVar[List[ToolSlotDefinition]] = []
tool_change_group: ClassVar[str] = ""
target_points: ClassVar[List[RemoteTcpDefinition]] = []
target_frames: ClassVar[List[TargetFrameDefinition]] = []
work_area_observers: ClassVar[List[WorkAreaObserverBinding]] = []
default_active_work_area_id: ClassVar[str] = ''
global_calibration_reference_frame: ClassVar[str] = 'calibration'
shell: ClassVar[ShellSetup] = ShellSetup()
role_policy: ClassVar[RolePolicy] = RolePolicy()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

```python
@property
def development_mode(self) -> bool
```

```python
def set_development_mode(self, enabled: bool) -> None
```

```python
@property
def system_manager(self)
```

```python
@property
def health_registry(self)
```

```python
def get_settings(self, name: Enum) -> Any
```

```python
def get_settings_repo(self, name: Enum) -> ISettingsRepository
```

```python
def get_service(self, name: Enum) -> Any
```

```python
def get_optional_service(self, name: Enum) -> Optional[Any]
```

```python
def get_targeting_provider(self)
```

```python
def get_work_area_definitions(self) -> List[WorkAreaDefinition]
```

```python
def get_movement_group_definitions(self) -> List[MovementGroupDefinition]
```

```python
def get_dispense_channel_definitions(self) -> List[DispenseChannelDefinition]
```

```python
def get_dispense_channel_definition(self, channel_id: str) -> DispenseChannelDefinition | None
```

```python
def get_tool_definitions(self) -> List[ToolDefinition]
```

```python
def get_tool_slot_definitions(self) -> List[ToolSlotDefinition]
```

```python
def get_tool_slot_definition(self, slot_id: int) -> ToolSlotDefinition | None
```

```python
def get_tool_slot_definition_for_tool(self, tool_id: int) -> ToolSlotDefinition | None
```

```python
def get_target_point_definitions(self) -> List[RemoteTcpDefinition]
```

```python
def get_target_point_definition(self, name: str) -> RemoteTcpDefinition | None
```

```python
def get_target_frame_definitions(self) -> List[TargetFrameDefinition]
```

```python
def get_target_frame_definition(self, name: str) -> TargetFrameDefinition | None
```

```python
def get_target_frame_for_work_area(self, work_area_id: str) -> TargetFrameDefinition | None
```

```python
def get_work_area_observer_bindings(self) -> List[WorkAreaObserverBinding]
```

```python
def get_default_active_work_area_id(self) -> str
```

```python
def get_observer_group_for_area(self, area_id: str) -> str | None
```

```python
def get_observed_area_for_group(self, movement_group_id: str) -> str | None
```

```python
def get_calibration_provider(self)
```

```python
def get_height_measuring_provider(self)
```

```python
def get_shared_vision_resolver(self)
```

```python
def invalidate_shared_vision_resolver(self) -> None
```

```python
def build_robot_system_jog_pose_resolver(self, reference_rz_provider=None)
```

```python
@classmethod
def package_root(cls) -> str
```

```python
@classmethod
def storage_path(cls, *parts: str) -> str
```

```python
@classmethod
def workpieces_storage_path(cls) -> str
```

```python
@classmethod
def users_storage_path(cls) -> str
```

```python
@classmethod
def permissions_storage_path(cls) -> str
```

```python
def register_managed_resource(self, resource: Any, cleanup: Any=None) -> Any
```

Register a generic runtime resource for automatic shutdown. Resources are cleaned up in reverse registration order after on_stop(). If cleanup is provided it is called directly. Otherwise the resource is inspected for stop/close/disconnect in that order.

```python
def unregister_managed_resource(self, resource: Any) -> None
```

```python
def start(self, services: Dict[str, Any], settings_service=None, system_manager=None, messaging_service=None) -> None
```

```python
def stop(self) -> None
```

```python
@property
def is_running(self) -> bool
```

```python
@abstractmethod
def on_start(self) -> None
```

```python
@abstractmethod
def on_stop(self) -> None
```

```python
@classmethod
def describe(cls) -> str
```

## `default_service_builders.py`

Source: [src/robot_systems/default_service_builders.py](../../src/robot_systems/default_service_builders.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `os`, `src.engine.common_service_ids`, `src.engine.common_settings_ids`, `src.engine.robot.features.navigation_service`, `src.engine.robot.interfaces.i_robot_service`, `src.engine.robot.interfaces.i_tool_service`, `src.engine.robot.services.robot_service`, `src.engine.robot.services.robot_state_manager`, `src.engine.robot.services.robot_state_publisher`, `src.engine.robot.tool_changer`, `src.engine.robot.tool_manager`, `src.engine.vision.i_vision_service`, `src.engine.vision.implementation.VisionSystem.VisionSystem`, `src.engine.vision.implementation.VisionSystem.core.service.internal_service`, `src.engine.vision.vision_service`, `src.engine.work_areas`.

Module declarations (expressions are shown without evaluating them):

```python
DEFAULT_SERVICE_BUILDERS = {IRobotService: build_robot_service, NavigationService: build_navigation_service, IWorkAreaService: build_work_area_service, IToolService: build_tool_service, IVisionService: build_vision_service}
```

### `build_robot_service`

```python
def build_robot_service(ctx) -> IRobotService
```

### `build_navigation_service`

```python
def build_navigation_service(ctx) -> NavigationService
```

### `build_tool_service`

```python
def build_tool_service(ctx)
```

Build the standard tool service from common tool and robot settings.

### `build_vision_service`

```python
def build_vision_service(ctx, *, camera_device: int | str | None=None, camera_resolution: tuple[int, int] | None=None, allow_camera_fallback: bool=True, camera_orientation: tuple[bool, bool, int]=(False, False, 0))
```

Build the standard vision service from common camera settings.

### `build_work_area_service`

```python
def build_work_area_service(ctx) -> IWorkAreaService
```

## `robot_system_bootstrap_provider.py`

Source: [src/robot_systems/robot_system_bootstrap_provider.py](../../src/robot_systems/robot_system_bootstrap_provider.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `abc`, `src.robot_systems.base_robot_system`, `typing`.

### `RobotSystemBootstrapProvider`

```python
class RobotSystemBootstrapProvider(ABC):
```

Robot-system-owned bootstrap composition for startup-only concerns.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
@abstractmethod
def system_class(self) -> Type[BaseRobotSystem]
```

```python
@abstractmethod
def build_robot(self)
```

```python
@abstractmethod
def build_login_view(self, robot_system: BaseRobotSystem, messaging_service)
```

```python
@abstractmethod
def build_authorization_service(self, robot_system: BaseRobotSystem)
```

## `system_builder.py`

Source: [src/robot_systems/system_builder.py](../../src/robot_systems/system_builder.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `logging`, `src.engine.common_settings_ids`, `src.engine.core.i_messaging_service`, `src.engine.core.messaging_service`, `src.engine.repositories.settings_service_factory`, `src.engine.robot.features.navigation_service`, `src.engine.robot.interfaces.i_motion_service`, `src.engine.robot.interfaces.i_robot`, `src.engine.robot.interfaces.i_robot_service`, `src.engine.robot.interfaces.i_tool_service`, `src.engine.robot.safety.safety_checker`, `src.engine.robot.services.motion_service`, `src.engine.system.system_manager`, `src.engine.vision.i_vision_service`, `src.engine.work_areas.i_work_area_service`, `src.robot_systems.base_robot_system`, `src.robot_systems.default_service_builders`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
T = TypeVar('T', bound=BaseRobotSystem)
ServiceBuilderFn = Callable[[_BuildContext], Optional[Any]]
```

### `_BuildContext`

```python
@dataclass
class _BuildContext:
```

Declared fields/defaults:

```python
robot: IRobot
motion: IMotionService
settings: Any
tool_changer: Any
messaging_service: IMessagingService
system_class: Type[BaseRobotSystem]
services: Dict[str, Any]
```

### `SystemBuilder`

```python
class SystemBuilder:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

```python
def with_robot(self, robot: IRobot) -> SystemBuilder
```

```python
def with_settings(self, settings_service) -> SystemBuilder
```

```python
def with_tool_changer(self, tool_changer) -> SystemBuilder
```

```python
def with_messaging_service(self, messaging_service: IMessagingService) -> SystemBuilder
```

```python
def with_development_mode(self, enabled: bool) -> SystemBuilder
```

```python
def register(self, service_type: Type, builder: ServiceBuilderFn) -> SystemBuilder
```

```python
def build(self, system_class: Type[T]) -> T
```
