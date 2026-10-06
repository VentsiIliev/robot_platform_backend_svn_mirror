# Module reference: `tests/applications/software_update`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_software_update.py](#test_software_updatepy)

## `__init__.py`

Source: [tests/applications/software_update/__init__.py](../../../../tests/applications/software_update/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_software_update.py`

Source: [tests/applications/software_update/test_software_update.py](../../../../tests/applications/software_update/test_software_update.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `json`, `os`, `pathlib`, `platform`, `src.applications.software_update.service.software_update_service`, `src.applications.software_update.service.stub_software_update_service`, `src.applications.software_update.software_update_factory`, `src.engine.localization.localization_service`, `tempfile`, `threading`, `time`, `unittest`, `unittest.mock`.

### `SoftwareUpdateTests`

```python
class SoftwareUpdateTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def setUp(self)
```

```python
def wait_done(self)
```

```python
def test_download_runs_off_gui_thread_then_updates_buttons(self)
```

```python
def test_install_schedules_and_does_not_quit_application(self)
```

```python
def test_check_displays_available_version(self)
```

```python
def test_up_to_date_check_shows_a_result_dialog(self)
```

```python
def test_disabled_updates_allow_check_and_show_configuration_error(self)
```

```python
def test_check_with_missing_configuration_reports_its_path(self)
```

```python
def test_check_reads_local_feed_and_displays_available_version(self)
```

```python
def test_previous_update_failure_is_displayed_after_restart(self)
```

```python
def test_process_gate_rejects_running_process(self)
```

```python
def test_initial_bulgarian_and_runtime_switch_preserve_status(self)
```
