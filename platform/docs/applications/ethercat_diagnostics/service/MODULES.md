# Module reference: `src/applications/ethercat_diagnostics/service`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [ethercat_diagnostics_application_service.py](#ethercat_diagnostics_application_servicepy)
- [i_ethercat_diagnostics_service.py](#i_ethercat_diagnostics_servicepy)
- [igh_ethercat_diagnostics_service.py](#igh_ethercat_diagnostics_servicepy)
- [stub_ethercat_diagnostics_service.py](#stub_ethercat_diagnostics_servicepy)

## `__init__.py`

Source: [src/applications/ethercat_diagnostics/service/__init__.py](../../../../src/applications/ethercat_diagnostics/service/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.ethercat_diagnostics.service.ethercat_diagnostics_application_service`, `src.applications.ethercat_diagnostics.service.i_ethercat_diagnostics_service`, `src.applications.ethercat_diagnostics.service.igh_ethercat_diagnostics_service`.

Package-level import/export surface:

```python
from src.applications.ethercat_diagnostics.service.ethercat_diagnostics_application_service import EthercatDiagnosticsApplicationService
from src.applications.ethercat_diagnostics.service.i_ethercat_diagnostics_service import EthercatDiagnosticsSnapshot, EthercatSlaveStatus, IEthercatDiagnosticsService
from src.applications.ethercat_diagnostics.service.igh_ethercat_diagnostics_service import IghEthercatDiagnosticsService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['EthercatDiagnosticsApplicationService', 'EthercatDiagnosticsSnapshot', 'EthercatSlaveStatus', 'IEthercatDiagnosticsService', 'IghEthercatDiagnosticsService']
```

## `ethercat_diagnostics_application_service.py`

Source: [src/applications/ethercat_diagnostics/service/ethercat_diagnostics_application_service.py](../../../../src/applications/ethercat_diagnostics/service/ethercat_diagnostics_application_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.ethercat_diagnostics.service.i_ethercat_diagnostics_service`, `typing`.

### `EthercatDiagnosticsApplicationService`

```python
class EthercatDiagnosticsApplicationService(IEthercatDiagnosticsService):
```

Normalizes EtherCAT diagnostics from a master-like provider. The provider is intentionally duck-typed. A future SOEM, IgH, ROS2, or vendor adapter can expose any of the generic methods below without changing the app layer.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, provider: object | None=None) -> None
```

```python
def refresh(self) -> EthercatDiagnosticsSnapshot
```

```python
def supports_reset_errors(self) -> bool
```

```python
def reset_errors(self) -> tuple[bool, str]
```

## `i_ethercat_diagnostics_service.py`

Source: [src/applications/ethercat_diagnostics/service/i_ethercat_diagnostics_service.py](../../../../src/applications/ethercat_diagnostics/service/i_ethercat_diagnostics_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `abc`, `dataclasses`, `typing`.

### `EthercatSlaveStatus`

```python
@dataclass(frozen=True)
class EthercatSlaveStatus:
```

Declared fields/defaults:

```python
slave_id: int | str
name: str = ''
state: str = 'unknown'
online: bool | None = None
operational: bool | None = None
error: str = ''
statusword: int | str | None = None
details: dict[str, Any] = field(default_factory=dict)
```

### `EthercatDiagnosticsSnapshot`

```python
@dataclass(frozen=True)
class EthercatDiagnosticsSnapshot:
```

Declared fields/defaults:

```python
master_state: str = 'unknown'
master_message: str = ''
slaves: tuple[EthercatSlaveStatus, ...] = ()
raw: dict[str, Any] = field(default_factory=dict)
```

### `IEthercatDiagnosticsService`

```python
class IEthercatDiagnosticsService(ABC):
```

Generic EtherCAT diagnostics contract, independent of a concrete master.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def refresh(self) -> EthercatDiagnosticsSnapshot
```

```python
def supports_reset_errors(self) -> bool
```

```python
def reset_errors(self) -> tuple[bool, str]
```

## `igh_ethercat_diagnostics_service.py`

Source: [src/applications/ethercat_diagnostics/service/igh_ethercat_diagnostics_service.py](../../../../src/applications/ethercat_diagnostics/service/igh_ethercat_diagnostics_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `re`, `shutil`, `src.applications.ethercat_diagnostics.service.i_ethercat_diagnostics_service`, `subprocess`, `typing`.

### `_CommandResult`

```python
@dataclass(frozen=True)
class _CommandResult:
```

Declared fields/defaults:

```python
args: tuple[str, ...]
returncode: int
stdout: str
stderr: str
```

### `IghEthercatDiagnosticsService`

```python
class IghEthercatDiagnosticsService(IEthercatDiagnosticsService):
```

EtherCAT diagnostics provider using the IgH `ethercat` command-line tool.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, *, executable: str='ethercat', master: str | None=None, timeout_s: float=2.0, runner: Callable[..., subprocess.CompletedProcess] | None=None) -> None
```

```python
def refresh(self) -> EthercatDiagnosticsSnapshot
```

```python
def supports_reset_errors(self) -> bool
```

```python
def reset_errors(self) -> tuple[bool, str]
```

```python
@classmethod
def parse_slaves(cls, output: str) -> list[EthercatSlaveStatus]
```

```python
@staticmethod
def parse_crc(output: str) -> dict
```

## `stub_ethercat_diagnostics_service.py`

Source: [src/applications/ethercat_diagnostics/service/stub_ethercat_diagnostics_service.py](../../../../src/applications/ethercat_diagnostics/service/stub_ethercat_diagnostics_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.ethercat_diagnostics.service.i_ethercat_diagnostics_service`.

### `StubEthercatDiagnosticsService`

```python
class StubEthercatDiagnosticsService(IEthercatDiagnosticsService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def refresh(self) -> EthercatDiagnosticsSnapshot
```

```python
def supports_reset_errors(self) -> bool
```

```python
def reset_errors(self) -> tuple[bool, str]
```
