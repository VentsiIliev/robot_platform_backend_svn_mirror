# Module reference: `src/applications/broker_debug/model`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [broker_debug_model.py](#broker_debug_modelpy)

## `__init__.py`

Source: [src/applications/broker_debug/model/__init__.py](../../../../src/applications/broker_debug/model/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `broker_debug_model.py`

Source: [src/applications/broker_debug/model/broker_debug_model.py](../../../../src/applications/broker_debug/model/broker_debug_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.i_application_model`, `src.applications.broker_debug.service.i_broker_debug_service`, `typing`.

### `BrokerDebugModel`

```python
class BrokerDebugModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IBrokerDebugService)
```

```python
def load(self) -> Dict[str, int]
```

```python
def save(self, *args, **kwargs) -> None
```

```python
def refresh(self) -> Dict[str, int]
```

```python
def publish(self, topic: str, message: str) -> None
```

```python
def subscribe_spy(self, topic: str, callback: Callable) -> None
```

```python
def unsubscribe_spy(self, topic: str, callback: Callable) -> None
```

```python
def clear_topic(self, topic: str) -> None
```
