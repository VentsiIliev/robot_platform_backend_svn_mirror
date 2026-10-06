# Module reference: `src/applications/APPLICATION_BLUEPRINT/service`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_my_service.py](#i_my_servicepy)
- [my_application_service.py](#my_application_servicepy)
- [stub_my_service.py](#stub_my_servicepy)

## `__init__.py`

Source: [src/applications/APPLICATION_BLUEPRINT/service/__init__.py](../../../../src/applications/APPLICATION_BLUEPRINT/service/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `i_my_service.py`

Source: [src/applications/APPLICATION_BLUEPRINT/service/i_my_service.py](../../../../src/applications/APPLICATION_BLUEPRINT/service/i_my_service.py).

Step 3 — Service interface. Defines ONLY what this application needs — not the full robot_app or settings_service. This is the boundary between the application and the rest of the platform. Rule: if you need data → add a query method. if you need an action → add a command method. Never pass ISettingsService or IRobotService directly into the application.

Imports (including optional/function-local imports; not a startup dependency list): `abc`.

### `IMyService`

```python
class IMyService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def get_value(self) -> str
```

Return a value the application needs to display.

```python
@abstractmethod
def save_value(self, value: str) -> None
```

Persist a user change.

## `my_application_service.py`

Source: [src/applications/APPLICATION_BLUEPRINT/service/my_application_service.py](../../../../src/applications/APPLICATION_BLUEPRINT/service/my_application_service.py).

Step 4 — Concrete service adapter. Implements IMyService by delegating to platform services (ISettingsService, IRobotService, etc.). This is the ONLY place that imports platform internals. The application never sees ISettingsService directly.

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.APPLICATION_BLUEPRINT.service.i_my_service`.

### `MyApplicationService`

```python
class MyApplicationService(IMyService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, settings_service=None)
```

```python
def get_value(self) -> str
```

```python
def save_value(self, value: str) -> None
```

## `stub_my_service.py`

Source: [src/applications/APPLICATION_BLUEPRINT/service/stub_my_service.py](../../../../src/applications/APPLICATION_BLUEPRINT/service/stub_my_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.APPLICATION_BLUEPRINT.service.i_my_service`.

### `StubMyService`

```python
class StubMyService(IMyService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def get_value(self) -> str
```

```python
def save_value(self, value: str) -> None
```
