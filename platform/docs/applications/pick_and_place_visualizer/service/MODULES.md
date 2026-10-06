# Module reference: `src/applications/pick_and_place_visualizer/service`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_pick_and_place_visualizer_service.py](#i_pick_and_place_visualizer_servicepy)
- [pick_and_place_visualizer_service.py](#pick_and_place_visualizer_servicepy)
- [stub_pick_and_place_visualizer_service.py](#stub_pick_and_place_visualizer_servicepy)

## `__init__.py`

Source: [src/applications/pick_and_place_visualizer/service/__init__.py](../../../../src/applications/pick_and_place_visualizer/service/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `i_pick_and_place_visualizer_service.py`

Source: [src/applications/pick_and_place_visualizer/service/i_pick_and_place_visualizer_service.py](../../../../src/applications/pick_and_place_visualizer/service/i_pick_and_place_visualizer_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `dataclasses`, `typing`.

### `MatchedItem`

```python
@dataclass
class MatchedItem:
```

Declared fields/defaults:

```python
workpiece_name: str
workpiece_id: str
gripper_id: int
orientation: float
```

### `PlacedItem`

```python
@dataclass
class PlacedItem:
```

Declared fields/defaults:

```python
workpiece_name: str
gripper_id: int
plane_x: float
plane_y: float
width: float
height: float
```

### `SimResult`

```python
@dataclass
class SimResult:
```

Declared fields/defaults:

```python
matched: List[MatchedItem] = field(default_factory=list)
placements: List[PlacedItem] = field(default_factory=list)
unmatched_count: int = 0
error: Optional[str] = None
```

### `IPickAndPlaceVisualizerService`

```python
class IPickAndPlaceVisualizerService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def run_simulation(self) -> SimResult
```

```python
@abstractmethod
def get_plane_bounds(self) -> Tuple[float, float, float, float, float]
```

```python
@abstractmethod
def set_simulation(self, value: bool) -> None
```

```python
@abstractmethod
def start_process(self) -> None
```

```python
@abstractmethod
def stop_process(self) -> None
```

```python
@abstractmethod
def pause_process(self) -> None
```

```python
@abstractmethod
def reset_process(self) -> None
```

```python
@abstractmethod
def get_process_state(self) -> str
```

```python
@abstractmethod
def set_step_mode(self, value: bool) -> None
```

```python
@abstractmethod
def is_step_mode_enabled(self) -> bool
```

```python
@abstractmethod
def step_process(self) -> None
```

## `pick_and_place_visualizer_service.py`

Source: [src/applications/pick_and_place_visualizer/service/pick_and_place_visualizer_service.py](../../../../src/applications/pick_and_place_visualizer/service/pick_and_place_visualizer_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.applications.pick_and_place_visualizer.service.i_pick_and_place_visualizer_service`, `src.engine.process.i_process`, `src.engine.vision.implementation.VisionSystem.core.models.contour`, `src.robot_systems.glue.domain.matching.i_matching_service`, `src.robot_systems.glue.processes.pick_and_place.config`, `src.robot_systems.glue.processes.pick_and_place.plane`, `src.robot_systems.glue.processes.pick_and_place.planning`, `typing`.

### `PickAndPlaceVisualizerService`

```python
class PickAndPlaceVisualizerService(IPickAndPlaceVisualizerService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, matching_service: IMatchingService, config: PickAndPlaceConfig, pick_and_place_process: Optional[IProcess]=None)
```

```python
def set_simulation(self, value: bool) -> None
```

```python
def start_process(self) -> None
```

```python
def stop_process(self) -> None
```

```python
def pause_process(self) -> None
```

```python
def reset_process(self) -> None
```

```python
def get_process_state(self) -> str
```

```python
def set_step_mode(self, value: bool) -> None
```

```python
def is_step_mode_enabled(self) -> bool
```

```python
def step_process(self) -> None
```

```python
def run_simulation(self) -> SimResult
```

```python
def get_plane_bounds(self) -> Tuple[float, float, float, float, float]
```

## `stub_pick_and_place_visualizer_service.py`

Source: [src/applications/pick_and_place_visualizer/service/stub_pick_and_place_visualizer_service.py](../../../../src/applications/pick_and_place_visualizer/service/stub_pick_and_place_visualizer_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.pick_and_place_visualizer.service.i_pick_and_place_visualizer_service`.

### `StubPickAndPlaceVisualizerService`

```python
class StubPickAndPlaceVisualizerService(IPickAndPlaceVisualizerService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def run_simulation(self) -> SimResult
```

```python
def get_plane_bounds(self)
```

```python
def start_process(self) -> None
```

```python
def stop_process(self) -> None
```

```python
def pause_process(self) -> None
```

```python
def reset_process(self) -> None
```

```python
def set_simulation(self, value: bool) -> None
```

```python
def get_process_state(self) -> str
```

```python
def set_step_mode(self, value: bool) -> None
```

```python
def is_step_mode_enabled(self) -> bool
```

```python
def step_process(self) -> None
```
