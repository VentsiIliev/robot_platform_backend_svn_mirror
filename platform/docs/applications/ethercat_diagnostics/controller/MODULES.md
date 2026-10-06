# Module reference: `src/applications/ethercat_diagnostics/controller`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [ethercat_diagnostics_controller.py](#ethercat_diagnostics_controllerpy)

## `__init__.py`

Source: [src/applications/ethercat_diagnostics/controller/__init__.py](../../../../src/applications/ethercat_diagnostics/controller/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.ethercat_diagnostics.controller.ethercat_diagnostics_controller`.

Package-level import/export surface:

```python
from src.applications.ethercat_diagnostics.controller.ethercat_diagnostics_controller import EthercatDiagnosticsController
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['EthercatDiagnosticsController']
```

## `ethercat_diagnostics_controller.py`

Source: [src/applications/ethercat_diagnostics/controller/ethercat_diagnostics_controller.py](../../../../src/applications/ethercat_diagnostics/controller/ethercat_diagnostics_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.applications.base.background_worker`, `src.applications.base.i_application_controller`, `src.applications.ethercat_diagnostics.model.ethercat_diagnostics_model`, `src.applications.ethercat_diagnostics.service.i_ethercat_diagnostics_service`, `src.applications.ethercat_diagnostics.view.ethercat_diagnostics_view`.

### `EthercatDiagnosticsController`

```python
class EthercatDiagnosticsController(IApplicationController, BackgroundWorker):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: EthercatDiagnosticsModel, view: EthercatDiagnosticsView) -> None
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```
