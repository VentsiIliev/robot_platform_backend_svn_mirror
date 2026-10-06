# Module reference: `src/applications/ethercat_diagnostics/view`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [ethercat_diagnostics_view.py](#ethercat_diagnostics_viewpy)

## `__init__.py`

Source: [src/applications/ethercat_diagnostics/view/__init__.py](../../../../src/applications/ethercat_diagnostics/view/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.ethercat_diagnostics.view.ethercat_diagnostics_view`.

Package-level import/export surface:

```python
from src.applications.ethercat_diagnostics.view.ethercat_diagnostics_view import EthercatDiagnosticsView
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['EthercatDiagnosticsView']
```

## `ethercat_diagnostics_view.py`

Source: [src/applications/ethercat_diagnostics/view/ethercat_diagnostics_view.py](../../../../src/applications/ethercat_diagnostics/view/ethercat_diagnostics_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `json`, `pl_gui.settings.settings_view.styles`, `src.applications.base.app_styles`, `src.applications.base.i_application_view`, `src.applications.ethercat_diagnostics.service.i_ethercat_diagnostics_service`.

### `EthercatDiagnosticsView`

```python
class EthercatDiagnosticsView(IApplicationView):
```

Declared fields/defaults:

```python
refresh_requested = pyqtSignal()
reset_errors_requested = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

```python
def setup_ui(self) -> None
```

```python
def clean_up(self) -> None
```

```python
def set_busy(self, busy: bool) -> None
```

```python
def set_reset_enabled(self, enabled: bool) -> None
```

```python
def set_status_message(self, message: str, *, ok: bool) -> None
```

```python
def set_snapshot(self, snapshot: EthercatDiagnosticsSnapshot) -> None
```
