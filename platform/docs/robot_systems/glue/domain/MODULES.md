# Module reference: `src/robot_systems/glue/domain`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [glue_job_builder_service.py](#glue_job_builder_servicepy)
- [glue_job_execution_service.py](#glue_job_execution_servicepy)
- [glue_workpiece_editor_adapter.py](#glue_workpiece_editor_adapterpy)

## `__init__.py`

Source: [src/robot_systems/glue/domain/__init__.py](../../../../src/robot_systems/glue/domain/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.glue.domain.glue_job_execution_service`.

Package-level import/export surface:

```python
from src.robot_systems.glue.domain.glue_job_execution_service import GlueExecutionResult, GlueJobExecutionService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['GlueExecutionResult', 'GlueJobExecutionService']
```

## `glue_job_builder_service.py`

Source: [src/robot_systems/glue/domain/glue_job_builder_service.py](../../../../src/robot_systems/glue/domain/glue_job_builder_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `src.engine.core.i_coordinate_transformer`, `src.engine.robot.targeting`, `typing`.

### `GlueJobBuildError`

```python
class GlueJobBuildError(ValueError):
```

### `GlueJobSegment`

```python
@dataclass(frozen=True)
class GlueJobSegment:
```

Declared fields/defaults:

```python
workpiece_id: str
pattern_type: str
segment_index: int
points: list[list[float]]
image_points: list[tuple[float, float]]
settings: dict[str, Any]
```

### `GlueJob`

```python
@dataclass(frozen=True)
class GlueJob:
```

Declared fields/defaults:

```python
segments: list[GlueJobSegment]
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def segment_count(self) -> int
```

```python
@property
def workpiece_count(self) -> int
```

### `GlueJobBuilderService`

```python
class GlueJobBuilderService:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, transformer: ICoordinateTransformer | None=None, resolver: VisionTargetResolver | None=None, resolver_getter: Callable[[], VisionTargetResolver | None] | None=None, z_min: float=0.0, target_point_name: str='') -> None
```

```python
def build_job(self, matched_workpieces: list[dict[str, Any]]) -> GlueJob
```

```python
def to_process_paths(self, job: GlueJob) -> list[tuple[list[list[float]], dict[str, Any], dict[str, Any]]]
```

## `glue_job_execution_service.py`

Source: [src/robot_systems/glue/domain/glue_job_execution_service.py](../../../../src/robot_systems/glue/domain/glue_job_execution_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `src.engine.core.i_messaging_service`, `src.engine.vision.i_capture_snapshot_service`, `src.shared_contracts.events.glue_overlay_events`, `threading`, `time`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
GlueExecutionStage = Literal['positioning', 'matching', 'job_build', 'load', 'start']
```

### `GlueExecutionResult`

```python
@dataclass(frozen=True)
class GlueExecutionResult:
```

Declared fields/defaults:

```python
success: bool
stage: GlueExecutionStage
message: str
matched_ids: list[str]
workpiece_count: int
segment_count: int
loaded: bool = False
started: bool = False
job_summary: dict[str, Any] | None = None
```

### `GlueJobExecutionService`

```python
class GlueJobExecutionService:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, matching_service, job_builder, glue_process, navigation_service=None, vision_service=None, robot_service=None, capture_snapshot_service: ICaptureSnapshotService | None=None, messaging_service: IMessagingService | None=None, stabilization_delay_s: float=0.5, sleep_fn=time.sleep) -> None
```

```python
def prepare_and_load(self, spray_on: bool) -> GlueExecutionResult
```

```python
def prepare_load_and_start(self, spray_on: bool) -> GlueExecutionResult
```

```python
def cancel_pending(self) -> bool
```

## `glue_workpiece_editor_adapter.py`

Source: [src/robot_systems/glue/domain/glue_workpiece_editor_adapter.py](../../../../src/robot_systems/glue/domain/glue_workpiece_editor_adapter.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `contour_editor.persistence.data.editor_data_model`, `logging`, `src.applications.workpiece_editor.editor_core.adapters.adapter_utils`, `src.applications.workpiece_editor.editor_core.adapters.i_workpiece_data_adapter`, `typing`.

### `GlueWorkpieceEditorAdapter`

```python
class GlueWorkpieceEditorAdapter(IWorkpieceDataAdapter):
```

Glue-specific editor adapter. Glue continues to own the ``sprayPattern`` mapping used by its persisted workpiece payloads. The generic editor only sees an injected adapter.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def from_workpiece(self, workpiece) -> ContourEditorData
```

```python
def to_workpiece_data(self, editor_data: ContourEditorData, default_settings: Optional[Dict[str, Any]]=None) -> Dict[str, Any]
```

```python
def from_raw(self, raw: dict) -> ContourEditorData
```

```python
def print_summary(self, editor_data: ContourEditorData) -> None
```
