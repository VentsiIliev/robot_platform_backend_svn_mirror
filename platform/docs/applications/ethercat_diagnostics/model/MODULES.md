# Module reference: `src/applications/ethercat_diagnostics/model`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [ethercat_diagnostics_model.py](#ethercat_diagnostics_modelpy)

## `__init__.py`

Source: [src/applications/ethercat_diagnostics/model/__init__.py](../../../../src/applications/ethercat_diagnostics/model/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.ethercat_diagnostics.model.ethercat_diagnostics_model`.

Package-level import/export surface:

```python
from src.applications.ethercat_diagnostics.model.ethercat_diagnostics_model import EthercatDiagnosticsModel
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['EthercatDiagnosticsModel']
```

## `ethercat_diagnostics_model.py`

Source: [src/applications/ethercat_diagnostics/model/ethercat_diagnostics_model.py](../../../../src/applications/ethercat_diagnostics/model/ethercat_diagnostics_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.base.i_application_model`, `src.applications.ethercat_diagnostics.service.i_ethercat_diagnostics_service`.

### `EthercatDiagnosticsModel`

```python
class EthercatDiagnosticsModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IEthercatDiagnosticsService) -> None
```

```python
def load(self) -> EthercatDiagnosticsSnapshot
```

```python
def save(self, *args, **kwargs) -> None
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
