# Module reference: `src/applications/workpiece_editor/service`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_workpiece_editor_service.py](#i_workpiece_editor_servicepy)
- [i_workpiece_path_executor.py](#i_workpiece_path_executorpy)
- [stub_workpiece_editor_service.py](#stub_workpiece_editor_servicepy)
- [workpiece_editor_service.py](#workpiece_editor_servicepy)

## `__init__.py`

Source: [src/applications/workpiece_editor/service/__init__.py](../../../../src/applications/workpiece_editor/service/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.workpiece_editor.service.i_workpiece_editor_service`, `src.applications.workpiece_editor.service.i_workpiece_path_executor`.

Package-level import/export surface:

```python
from src.applications.workpiece_editor.service.i_workpiece_editor_service import IWorkpieceEditorService
from src.applications.workpiece_editor.service.i_workpiece_path_executor import IWorkpiecePathExecutor
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `i_workpiece_editor_service.py`

Source: [src/applications/workpiece_editor/service/i_workpiece_editor_service.py](../../../../src/applications/workpiece_editor/service/i_workpiece_editor_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `src.applications.workpiece_editor.editor_core.adapters.i_workpiece_data_adapter`, `src.applications.workpiece_editor.editor_core.config.segment_editor_config`, `src.applications.workpiece_editor.editor_core.config.workpiece_form_schema`, `src.applications.workpiece_editor.service.i_workpiece_path_executor`, `typing`.

### `IWorkpieceEditorService`

```python
class IWorkpieceEditorService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def get_workpiece_data_adapter(self) -> IWorkpieceDataAdapter
```

```python
@abstractmethod
def get_form_schema(self) -> WorkpieceFormSchema
```

```python
@abstractmethod
def get_segment_config(self) -> SegmentEditorConfig
```

```python
@abstractmethod
def get_contours(self) -> list
```

```python
@abstractmethod
def save_workpiece(self, data: dict) -> tuple[bool, str]
```

```python
@abstractmethod
def execute_workpiece(self, data: dict, skip_debug_plot: bool=False) -> tuple[bool, str]
```

```python
@abstractmethod
def get_last_sampled_preview_paths(self) -> list
```

```python
@abstractmethod
def get_last_raw_preview_paths(self) -> list
```

```python
@abstractmethod
def get_last_raw_pixel_preview_paths(self) -> list
```

```python
@abstractmethod
def get_last_raw_homography_preview_paths(self) -> list
```

```python
@abstractmethod
def get_last_prepared_preview_paths(self) -> list
```

```python
@abstractmethod
def get_last_curve_preview_paths(self) -> list
```

```python
@abstractmethod
def get_last_execution_preview_paths(self) -> list
```

```python
@abstractmethod
def get_last_projection_source_camera_paths(self) -> list
```

```python
@abstractmethod
def get_last_projection_source_paths(self) -> list
```

```python
@abstractmethod
def get_last_camera_preview_paths(self) -> dict[str, list]
```

```python
@abstractmethod
def get_last_pivot_preview_paths(self) -> tuple[list[list[list[float]]], list[float] | None]
```

```python
@abstractmethod
def get_last_pivot_motion_preview(self) -> tuple[list, list[float] | None]
```

```python
@abstractmethod
def get_process_actions(self) -> tuple[WorkpieceProcessAction, ...]
```

```python
@abstractmethod
def execute_process_action(self, action_id: str) -> tuple[bool, str]
```

```python
@abstractmethod
def set_editing(self, storage_id: Optional[str]) -> None
```

Pass storage_id to edit an existing workpiece on the next save, or None for new.

```python
@abstractmethod
def can_match_saved_workpieces(self) -> bool
```

```python
@abstractmethod
def match_saved_workpieces(self, contour) -> tuple[bool, dict | None, str]
```

## `i_workpiece_path_executor.py`

Source: [src/applications/workpiece_editor/service/i_workpiece_path_executor.py](../../../../src/applications/workpiece_editor/service/i_workpiece_path_executor.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `dataclasses`, `numpy`, `src.engine.robot.path_preparation`, `typing`.

### `WorkpieceProcessAction`

```python
@dataclass(frozen=True)
class WorkpieceProcessAction:
```

One executor-owned process action that the editor can present generically.

Declared fields/defaults:

```python
action_id: str
label: str
requires_projected_path_plot: bool = False
```

### `IWorkpiecePathExecutor`

```python
class IWorkpiecePathExecutor(ABC):
```

Robot-system-owned execution adapter for prepared workpiece paths.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def prepare_workpiece_execution_plan(self, workpiece: dict, skip_debug_plot: bool=False) -> 'WorkpieceExecutionPlan'
```

Optionally let the robot-system executor own workpiece-to-execution-plan preparation.

```python
def prepare_workpiece_preview(self, workpiece: dict, skip_debug_plot: bool=False) -> 'WorkpieceExecutionPlan'
```

Backward-compatible alias for editor preview callers.

```python
def get_last_execution_plan(self) -> 'WorkpieceExecutionPlan | None'
```

Optionally expose the executor-owned execution plan cache.

```python
def get_process_actions(self) -> tuple[WorkpieceProcessAction, ...]
```

Expose executor-owned process actions for the editor UI.

```python
def execute_process_action(self, execution_plan: 'WorkpieceExecutionPlan', action_id: str) -> tuple[bool, str]
```

Execute one executor-owned process action.

```python
@abstractmethod
def get_supported_execution_modes(self) -> tuple[str, ...]
```

```python
@abstractmethod
def get_projected_pivot_paths(self, execution_plan: 'WorkpieceExecutionPlan') -> tuple[list[list[list[float]]], list[float] | None]
```

```python
def get_pivot_preview_paths(self, execution_plan: 'WorkpieceExecutionPlan') -> tuple[list[list[list[float]]], list[float] | None]
```

Backward-compatible alias for editor preview callers.

```python
@abstractmethod
def get_pivot_motion_snapshots(self, execution_plan: 'WorkpieceExecutionPlan') -> tuple[list[list[np.ndarray]], list[float] | None]
```

```python
def get_pivot_motion_preview(self, execution_plan: 'WorkpieceExecutionPlan') -> tuple[list[list[np.ndarray]], list[float] | None]
```

Backward-compatible alias for editor preview callers.

```python
@abstractmethod
def execute_process_paths(self, execution_plan: 'WorkpieceExecutionPlan', mode: str='continuous') -> tuple[bool, str]
```

```python
def execute_preview_paths(self, execution_plan: 'WorkpieceExecutionPlan', mode: str='continuous') -> tuple[bool, str]
```

Backward-compatible alias for older executor callers.

```python
def execute_paint_process(self, execution_plan: 'WorkpieceExecutionPlan') -> tuple[bool, str]
```

Paint-specific full-process entry point when supported by the robot system.

## `stub_workpiece_editor_service.py`

Source: [src/applications/workpiece_editor/service/stub_workpiece_editor_service.py](../../../../src/applications/workpiece_editor/service/stub_workpiece_editor_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `contour_editor.persistence.data.editor_data_model`, `logging`, `src.applications.workpiece_editor.editor_core.adapters.i_workpiece_data_adapter`, `src.applications.workpiece_editor.editor_core.config.segment_editor_config`, `src.applications.workpiece_editor.editor_core.config.workpiece_form_schema`, `src.applications.workpiece_editor.service`, `src.applications.workpiece_editor.service.i_workpiece_path_executor`.

### `_StubWorkpieceDataAdapter`

```python
class _StubWorkpieceDataAdapter(IWorkpieceDataAdapter):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def from_workpiece(self, workpiece) -> ContourEditorData
```

```python
def to_workpiece_data(self, editor_data: ContourEditorData, default_settings=None) -> dict
```

```python
def from_raw(self, raw: dict) -> ContourEditorData
```

```python
def print_summary(self, editor_data: ContourEditorData) -> None
```

### `StubWorkpieceEditorService`

```python
class StubWorkpieceEditorService(IWorkpieceEditorService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, form_schema: WorkpieceFormSchema, segment_config: SegmentEditorConfig)
```

```python
def get_workpiece_data_adapter(self) -> IWorkpieceDataAdapter
```

```python
def get_form_schema(self) -> WorkpieceFormSchema
```

```python
def get_segment_config(self) -> SegmentEditorConfig
```

```python
def get_contours(self) -> list
```

```python
def save_workpiece(self, data: dict) -> tuple[bool, str]
```

```python
def execute_workpiece(self, data: dict, skip_debug_plot: bool=False) -> tuple[bool, str]
```

```python
def get_process_actions(self) -> tuple[WorkpieceProcessAction, ...]
```

```python
def execute_process_action(self, action_id: str) -> tuple[bool, str]
```

```python
def get_last_sampled_preview_paths(self) -> list
```

```python
def get_last_raw_preview_paths(self) -> list
```

```python
def get_last_raw_pixel_preview_paths(self) -> list
```

```python
def get_last_raw_homography_preview_paths(self) -> list
```

```python
def get_last_prepared_preview_paths(self) -> list
```

```python
def get_last_curve_preview_paths(self) -> list
```

```python
def get_last_execution_preview_paths(self) -> list
```

```python
def get_last_projection_source_camera_paths(self) -> list
```

```python
def get_last_projection_source_paths(self) -> list
```

```python
def get_last_camera_preview_paths(self) -> dict[str, list]
```

```python
def get_last_pivot_preview_paths(self) -> tuple[list[list[list[float]]], list[float] | None]
```

```python
def get_last_pivot_motion_preview(self)
```

```python
def set_editing(self, storage_id) -> None
```

```python
def can_match_saved_workpieces(self) -> bool
```

```python
def match_saved_workpieces(self, contour) -> tuple[bool, dict | None, str]
```

## `workpiece_editor_service.py`

Source: [src/applications/workpiece_editor/service/workpiece_editor_service.py](../../../../src/applications/workpiece_editor/service/workpiece_editor_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `contour_editor.persistence.data.editor_data_model`, `dataclasses`, `datetime`, `logging`, `os`, `src.applications.workpiece_editor.editor_core.adapters.i_workpiece_data_adapter`, `src.applications.workpiece_editor.editor_core.config`, `src.applications.workpiece_editor.editor_core.config.segment_editor_config`, `src.applications.workpiece_editor.editor_core.handlers.SaveWorkpieceHandler`, `src.applications.workpiece_editor.i_workpiece_matcher`, `src.applications.workpiece_editor.service`, `src.applications.workpiece_editor.service.i_workpiece_path_executor`, `src.engine.core.i_coordinate_transformer`, `src.engine.robot.path_preparation`, `src.engine.robot.path_preparation.geometry`, `src.engine.vision.capture_snapshot_service`, `src.engine.vision.i_capture_snapshot_service`, `typing`.

### `WorkpieceEditorStorage`

```python
@dataclass(frozen=True)
class WorkpieceEditorStorage:
```

Declared fields/defaults:

```python
save_fn: Callable[[dict], tuple[bool, str]]
update_fn: Callable[[str, dict], tuple[bool, str]]
id_exists_fn: Optional[Callable[[str], bool]] = None
```

### `WorkpieceEditorServices`

```python
@dataclass(frozen=True)
class WorkpieceEditorServices:
```

Declared fields/defaults:

```python
vision_service: object = None
capture_snapshot_service: Optional[ICaptureSnapshotService] = None
robot_service: object = None
transformer: Optional[ICoordinateTransformer] = None
transformer_getter: Optional[Callable[[], Optional[ICoordinateTransformer]]] = None
path_executor: Optional[IWorkpiecePathExecutor] = None
path_preparation_service: Optional[IWorkpiecePathPreparationService] = None
matching_service: Optional[IWorkpieceMatcher] = None
workpiece_data_adapter: Optional[IWorkpieceDataAdapter] = None
process_execution_validator: Optional[Callable[[], tuple[bool, str]]] = None
```

### `WorkpieceEditorOptions`

```python
@dataclass(frozen=True)
class WorkpieceEditorOptions:
```

Declared fields/defaults:

```python
debug_dump_dir: Optional[str] = None
```

### `WorkpieceEditorService`

```python
class WorkpieceEditorService(IWorkpieceEditorService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, *, storage: WorkpieceEditorStorage, services: WorkpieceEditorServices, form_schema: WorkpieceFormSchema, segment_config: SegmentEditorConfig, options: WorkpieceEditorOptions | None=None)
```

```python
def get_workpiece_data_adapter(self) -> IWorkpieceDataAdapter
```

```python
def set_editing(self, storage_id) -> None
```

```python
def get_form_schema(self) -> WorkpieceFormSchema
```

```python
def get_segment_config(self) -> SegmentEditorConfig
```

```python
def can_match_saved_workpieces(self) -> bool
```

```python
def match_saved_workpieces(self, contour) -> tuple[bool, dict | None, str]
```

```python
def get_contours(self) -> list
```

```python
def save_workpiece(self, data: dict) -> tuple[bool, str]
```

```python
def execute_workpiece(self, data: dict, skip_debug_plot: bool=False) -> tuple[bool, str]
```

```python
def get_last_sampled_preview_paths(self) -> list
```

```python
def get_last_raw_preview_paths(self) -> list
```

```python
def get_last_raw_pixel_preview_paths(self) -> list
```

```python
def get_last_raw_homography_preview_paths(self) -> list
```

```python
def get_last_prepared_preview_paths(self) -> list
```

```python
def get_last_curve_preview_paths(self) -> list
```

```python
def get_last_execution_preview_paths(self) -> list
```

```python
def get_last_projection_source_camera_paths(self) -> list
```

Return the exact ordered contours consumed by paint projection, in pixels.

```python
def get_last_projection_source_paths(self) -> list
```

Return exact robot-space paths passed to paint-contact projection.

```python
def get_last_camera_preview_paths(self) -> dict[str, list]
```

```python
def get_last_pivot_preview_paths(self) -> tuple[list[list[list[float]]], list[float] | None]
```

```python
def get_last_pivot_motion_preview(self)
```

```python
def get_process_actions(self) -> tuple[WorkpieceProcessAction, ...]
```

```python
def execute_process_action(self, action_id: str) -> tuple[bool, str]
```

### `_safe_float`

```python
def _safe_float(value, default: float) -> float
```
