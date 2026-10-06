# Module reference: `src/applications/ethercat_diagnostics`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [ethercat_diagnostics_factory.py](#ethercat_diagnostics_factorypy)
- [example_usage.py](#example_usagepy)

## `__init__.py`

Source: [src/applications/ethercat_diagnostics/__init__.py](../../../src/applications/ethercat_diagnostics/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.ethercat_diagnostics.ethercat_diagnostics_factory`, `src.applications.ethercat_diagnostics.service.i_ethercat_diagnostics_service`.

Package-level import/export surface:

```python
from src.applications.ethercat_diagnostics.ethercat_diagnostics_factory import EthercatDiagnosticsFactory
from src.applications.ethercat_diagnostics.service.i_ethercat_diagnostics_service import EthercatDiagnosticsSnapshot, EthercatSlaveStatus, IEthercatDiagnosticsService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['EthercatDiagnosticsFactory', 'EthercatDiagnosticsSnapshot', 'EthercatSlaveStatus', 'IEthercatDiagnosticsService']
```

## `ethercat_diagnostics_factory.py`

Source: [src/applications/ethercat_diagnostics/ethercat_diagnostics_factory.py](../../../src/applications/ethercat_diagnostics/ethercat_diagnostics_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.base.application_factory`, `src.applications.base.i_application_controller`, `src.applications.base.i_application_model`, `src.applications.base.i_application_view`, `src.applications.ethercat_diagnostics.controller.ethercat_diagnostics_controller`, `src.applications.ethercat_diagnostics.model.ethercat_diagnostics_model`, `src.applications.ethercat_diagnostics.service.i_ethercat_diagnostics_service`, `src.applications.ethercat_diagnostics.view.ethercat_diagnostics_view`.

### `EthercatDiagnosticsFactory`

```python
class EthercatDiagnosticsFactory(ApplicationFactory):
```

## `example_usage.py`

Source: [src/applications/ethercat_diagnostics/example_usage.py](../../../src/applications/ethercat_diagnostics/example_usage.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `__future__`, `src.applications.ethercat_diagnostics.ethercat_diagnostics_factory`, `src.applications.ethercat_diagnostics.service.stub_ethercat_diagnostics_service`, `sys`.

### `run_standalone`

```python
def run_standalone() -> None
```
