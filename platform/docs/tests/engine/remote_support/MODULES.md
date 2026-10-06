# Module reference: `tests/engine/remote_support`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_controller.py](#test_controllerpy)
- [test_expiry.py](#test_expirypy)
- [test_password_client.py](#test_password_clientpy)
- [test_session_client.py](#test_session_clientpy)
- [test_shell_monitor.py](#test_shell_monitorpy)

## `__init__.py`

Source: [tests/engine/remote_support/__init__.py](../../../../tests/engine/remote_support/__init__.py).

Remote support engine tests.

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_controller.py`

Source: [tests/engine/remote_support/test_controller.py](../../../../tests/engine/remote_support/test_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `pathlib`, `socket`, `src.applications.network_settings.service.remote_support_client`, `src.engine.remote_support`, `subprocess`, `tempfile`, `threading`, `unittest`, `unittest.mock`.

### `RemoteSupportControllerTests`

```python
class RemoteSupportControllerTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_protocol_rejects_arbitrary_commands(self) -> None
```

```python
def test_enable_marker_precedes_start_and_disable_removes_it_before_stop(self) -> None
```

```python
def test_status_rejects_missing_unit(self) -> None
```

```python
def test_failed_enable_restores_off_marker(self) -> None
```

```python
def test_client_and_controller_exchange_status_over_unix_socket(self) -> None
```

## `test_expiry.py`

Source: [tests/engine/remote_support/test_expiry.py](../../../../tests/engine/remote_support/test_expiry.py).

Imports (including optional/function-local imports; not a startup dependency list): `json`, `pathlib`, `src.engine.remote_support`, `subprocess`, `tempfile`, `unittest`, `unittest.mock`.

### `AccessExpiryTests`

```python
class AccessExpiryTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def systemctl(self, *args)
```

```python
def test_every_preset_expires_without_a_gui_or_status_request(self)
```

```python
def test_controller_restart_and_repeated_enable_do_not_extend_deadline(self)
```

```python
def test_reboot_and_legacy_marker_cannot_restart_remote_support(self)
```

```python
def test_failed_stop_is_retried_after_permission_marker_removed(self)
```

```python
def test_invalid_durations_and_extra_parameters_have_no_side_effects(self)
```

## `test_password_client.py`

Source: [tests/engine/remote_support/test_password_client.py](../../../../tests/engine/remote_support/test_password_client.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.remote_support.password_client`, `unittest`, `unittest.mock`.

### `PasswordClientTests`

```python
class PasswordClientTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def daemon(self, request)
```

```python
def test_setting_password_requires_ack_and_preserves_unrelated_options(self)
```

```python
def test_rejected_change_does_not_enable_unattended_access(self)
```

```python
def test_removal_disables_password_login_even_with_branded_preset(self)
```

```python
def test_ipc_failure_never_exposes_secret_in_error(self)
```

## `test_session_client.py`

Source: [tests/engine/remote_support/test_session_client.py](../../../../tests/engine/remote_support/test_session_client.py).

Imports (including optional/function-local imports; not a startup dependency list): `json`, `src.engine.remote_support.session_client`, `unittest`, `unittest.mock`.

### `_Socket`

```python
class _Socket:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, response)
```

```python
def settimeout(self, _)
```

```python
def connect(self, path)
```

```python
def sendall(self, data)
```

```python
def recv(self, length)
```

### `RustDeskSessionClientTests`

```python
class RustDeskSessionClientTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def query(self, response, width=1)
```

```python
def test_authenticated_counts_and_partial_frames(self)
```

```python
def test_invalid_responses_never_become_zero(self)
```

```python
def test_truncated_and_oversized_frames_are_rejected(self)
```

```python
def test_password_request_uses_multibyte_frame_header(self)
```

## `test_shell_monitor.py`

Source: [tests/engine/remote_support/test_shell_monitor.py](../../../../tests/engine/remote_support/test_shell_monitor.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `json`, `os`, `pathlib`, `pl_gui.shell.ui.Header`, `src.bootstrap.shell_remote_support_controller`, `time`, `unittest`, `unittest.mock`.

### `_Translator`

```python
class _Translator(QTranslator):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def isEmpty(self)
```

```python
def translate(self, context, source, disambiguation=None, n=-1)
```

### `ShellRemoteSupportTests`

```python
class ShellRemoteSupportTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_worker_distinguishes_service_from_sessions_and_failures(self)
```

```python
def test_background_monitor_updates_header_and_stops(self)
```

```python
def test_badge_visibility_and_initial_and_runtime_translation(self)
```
