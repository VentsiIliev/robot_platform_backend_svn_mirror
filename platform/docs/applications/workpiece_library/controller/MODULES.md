# Module reference: `src/applications/workpiece_library/controller`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [workpiece_library_controller.py](#workpiece_library_controllerpy)

## `__init__.py`

Source: [src/applications/workpiece_library/controller/__init__.py](../../../../src/applications/workpiece_library/controller/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.workpiece_library_controller`.

Package-level import/export surface:

```python
from .workpiece_library_controller import WorkpieceLibraryController
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `workpiece_library_controller.py`

Source: [src/applications/workpiece_library/controller/workpiece_library_controller.py](../../../../src/applications/workpiece_library/controller/workpiece_library_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `collections`, `logging`, `src.applications.base.i_application_controller`, `src.applications.base.styled_message_box`, `src.applications.workpiece_library.domain`, `src.applications.workpiece_library.model.workpiece_library_model`, `src.applications.workpiece_library.view.workpiece_library_view`, `src.engine.core.i_messaging_service`, `src.shared_contracts.events.shell_events`, `src.shared_contracts.events.workpiece_events`.

### `WorkpieceLibraryController`

```python
class WorkpieceLibraryController(IApplicationController):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: WorkpieceLibraryModel, view: WorkpieceLibraryView, messaging: IMessagingService)
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```
