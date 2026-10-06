# Module reference: `src/applications/workpiece_library`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [example_usage.py](#example_usagepy)
- [workpiece_library_factory.py](#workpiece_library_factorypy)
- [workpiece_thumbnail.py](#workpiece_thumbnailpy)

## `__init__.py`

Source: [src/applications/workpiece_library/__init__.py](../../../src/applications/workpiece_library/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.workpiece_library.service.i_workpiece_library_service`, `src.applications.workpiece_library.workpiece_library_factory`.

Package-level import/export surface:

```python
from src.applications.workpiece_library.service.i_workpiece_library_service import IWorkpieceLibraryService
from src.applications.workpiece_library.workpiece_library_factory import WorkpieceLibraryFactory
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `example_usage.py`

Source: [src/applications/workpiece_library/example_usage.py](../../../src/applications/workpiece_library/example_usage.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `logging`, `os`, `src.applications.workpiece_library.service.stub_workpiece_library_service`, `src.applications.workpiece_library.workpiece_library_factory`, `sys`.

### `run_standalone`

```python
def run_standalone()
```

## `workpiece_library_factory.py`

Source: [src/applications/workpiece_library/workpiece_library_factory.py](../../../src/applications/workpiece_library/workpiece_library_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.application_factory`, `src.applications.base.i_application_controller`, `src.applications.base.i_application_model`, `src.applications.base.i_application_view`, `src.applications.workpiece_library.controller.workpiece_library_controller`, `src.applications.workpiece_library.model.workpiece_library_model`, `src.applications.workpiece_library.service.i_workpiece_library_service`, `src.applications.workpiece_library.service.i_workpiece_selection`, `src.applications.workpiece_library.view.workpiece_library_view`, `src.engine.core.i_messaging_service`.

### `WorkpieceLibraryFactory`

```python
class WorkpieceLibraryFactory(ApplicationFactory):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def build(self, service: IWorkpieceLibraryService, messaging: IMessagingService=None, jog_service=None, selection: IWorkpieceSelection | None=None)
```

## `workpiece_thumbnail.py`

Source: [src/applications/workpiece_library/workpiece_thumbnail.py](../../../src/applications/workpiece_library/workpiece_thumbnail.py).

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `logging`, `numpy`, `typing`.

### `generate_thumbnail_bytes`

```python
def generate_thumbnail_bytes(raw: dict, size: int=_CANVAS) -> Optional[bytes]
```

### `_points_from`

```python
def _points_from(data) -> List[Tuple[float, float]]
```

### `_extract_points`

```python
def _extract_points(data) -> List[Tuple[float, float]]
```

### `_fit_transform`

```python
def _fit_transform(pts: List[Tuple[float, float]], size: int)
```

### `_to_cv`

```python
def _to_cv(pts: List[Tuple[float, float]], xf, yf) -> np.ndarray
```
