# Module reference: `src/applications/broker_debug/controller`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [broker_debug_controller.py](#broker_debug_controllerpy)

## `__init__.py`

Source: [src/applications/broker_debug/controller/__init__.py](../../../../src/applications/broker_debug/controller/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `broker_debug_controller.py`

Source: [src/applications/broker_debug/controller/broker_debug_controller.py](../../../../src/applications/broker_debug/controller/broker_debug_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `html`, `logging`, `src.applications.base.i_application_controller`, `src.applications.broker_debug.model.broker_debug_model`, `src.applications.broker_debug.view.broker_debug_view`, `src.engine.core.i_messaging_service`, `typing`.

### `_Bridge`

```python
class _Bridge(QObject):
```

Declared fields/defaults:

```python
message_received = pyqtSignal(str, object)
```

### `_SpyCallback`

```python
class _SpyCallback:
```

Bound-method wrapper — keeps the callback alive and usable with WeakMethod.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, topic: str, bridge: _Bridge)
```

### `BrokerDebugController`

```python
class BrokerDebugController(IApplicationController):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: BrokerDebugModel, view: BrokerDebugView, messaging: IMessagingService)
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```
