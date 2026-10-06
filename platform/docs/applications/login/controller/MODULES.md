# Module reference: `src/applications/login/controller`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [login_controller.py](#login_controllerpy)

## `__init__.py`

Source: [src/applications/login/controller/__init__.py](../../../../src/applications/login/controller/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `login_controller.py`

Source: [src/applications/login/controller/login_controller.py](../../../../src/applications/login/controller/login_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `src.applications.login.model.login_model`, `src.engine.core.i_messaging_service`, `src.shared_contracts.events.vision_events`, `typing`.

### `_Bridge`

```python
class _Bridge(QObject):
```

Safely delivers camera frames from the broker thread to the Qt thread.

Declared fields/defaults:

```python
camera_frame = pyqtSignal(object)
```

### `LoginController`

```python
class LoginController:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: LoginModel, view, messaging: Optional[IMessagingService]=None) -> None
```

```python
def load(self) -> None
```
