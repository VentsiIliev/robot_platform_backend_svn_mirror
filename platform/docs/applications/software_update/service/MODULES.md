# Module reference: `src/applications/software_update/service`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [i_software_update_service.py](#i_software_update_servicepy)
- [software_update_service.py](#software_update_servicepy)
- [stub_software_update_service.py](#stub_software_update_servicepy)

## `i_software_update_service.py`

Source: [src/applications/software_update/service/i_software_update_service.py](../../../../src/applications/software_update/service/i_software_update_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`.

### `ISoftwareUpdateService`

```python
class ISoftwareUpdateService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def get_status(self) -> dict
```

Return installed/staged versions and configuration location.

```python
@abstractmethod
def check(self) -> dict
```

Return the authenticated latest release and availability.

```python
@abstractmethod
def download(self) -> dict
```

Download and stage the latest verified platform release.

```python
@abstractmethod
def schedule_installation(self) -> None
```

Queue activation after the managed application has closed.

## `software_update_service.py`

Source: [src/applications/software_update/service/software_update_service.py](../../../../src/applications/software_update/service/software_update_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `.i_software_update_service`, `json`, `src.engine.updates.config`, `src.engine.updates.updater`.

### `SoftwareUpdateService`

```python
class SoftwareUpdateService(ISoftwareUpdateService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, can_schedule)
```

```python
def get_status(self) -> dict
```

```python
def check(self) -> dict
```

```python
def download(self) -> dict
```

```python
def schedule_installation(self) -> None
```

## `stub_software_update_service.py`

Source: [src/applications/software_update/service/stub_software_update_service.py](../../../../src/applications/software_update/service/stub_software_update_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `.i_software_update_service`.

### `StubSoftwareUpdateService`

```python
class StubSoftwareUpdateService(ISoftwareUpdateService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def get_status(self)
```

```python
def check(self)
```

```python
def download(self)
```

```python
def schedule_installation(self)
```
