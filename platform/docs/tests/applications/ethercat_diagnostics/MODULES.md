# Module reference: `tests/applications/ethercat_diagnostics`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [test_ethercat_diagnostics_service.py](#test_ethercat_diagnostics_servicepy)
- [test_igh_ethercat_diagnostics_service.py](#test_igh_ethercat_diagnostics_servicepy)

## `test_ethercat_diagnostics_service.py`

Source: [tests/applications/ethercat_diagnostics/test_ethercat_diagnostics_service.py](../../../../tests/applications/ethercat_diagnostics/test_ethercat_diagnostics_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.ethercat_diagnostics.service.ethercat_diagnostics_application_service`, `unittest`.

### `_GenericProvider`

```python
class _GenericProvider:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def get_ethercat_diagnostics(self)
```

### `_DriveStatusProvider`

```python
class _DriveStatusProvider:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def get_drive_status(self)
```

### `_ErrorProvider`

```python
class _ErrorProvider:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def get_drive_status(self)
```

### `TestEthercatDiagnosticsService`

```python
class TestEthercatDiagnosticsService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_normalizes_generic_master_slaves(self) -> None
```

```python
def test_normalizes_drive_status_fallback_as_slaves(self) -> None
```

```python
def test_reports_provider_error_payload(self) -> None
```

## `test_igh_ethercat_diagnostics_service.py`

Source: [tests/applications/ethercat_diagnostics/test_igh_ethercat_diagnostics_service.py](../../../../tests/applications/ethercat_diagnostics/test_igh_ethercat_diagnostics_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.ethercat_diagnostics.service.igh_ethercat_diagnostics_service`, `subprocess`, `unittest`, `unittest.mock`.

### `TestIghEthercatDiagnosticsService`

```python
class TestIghEthercatDiagnosticsService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_parse_slaves_normal_output(self) -> None
```

```python
def test_refresh_runs_master_slaves_and_crc(self) -> None
```

```python
def test_reset_errors_uses_crc_reset(self) -> None
```
