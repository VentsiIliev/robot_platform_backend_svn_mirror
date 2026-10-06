# Module reference: `src/engine/remote_support`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [client.py](#clientpy)
- [controller.py](#controllerpy)
- [password_client.py](#password_clientpy)
- [session_client.py](#session_clientpy)

## `__init__.py`

Source: [src/engine/remote_support/__init__.py](../../../src/engine/remote_support/__init__.py).

Local privileged control for robot remote support.

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `client.py`

Source: [src/engine/remote_support/client.py](../../../src/engine/remote_support/client.py).

Unprivileged client for the local PL PROJECT remote support controller.

Imports (including optional/function-local imports; not a startup dependency list): `json`, `socket`, `time`.

Module declarations (expressions are shown without evaluating them):

```python
SOCKET_PATH = '/run/plproject/remote-support.sock'
MAX_RESPONSE_BYTES = 4096
```

### `RemoteSupportClient`

```python
class RemoteSupportClient:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, socket_path: str=SOCKET_PATH, timeout: float=100) -> None
```

```python
def status(self) -> dict
```

```python
def set_enabled(self, enabled: bool, duration_seconds: int | None=None) -> dict
```

## `controller.py`

Source: [src/engine/remote_support/controller.py](../../../src/engine/remote_support/controller.py).

Local, socket-activated controller for the system RustDesk unit. Installed outside the application and run by systemd as root. The request protocol deliberately has no command, unit-name, or path parameters.

Imports (including optional/function-local imports; not a startup dependency list): `fcntl`, `json`, `logging`, `math`, `os`, `pathlib`, `socket`, `subprocess`, `sys`, `time`.

Module declarations (expressions are shown without evaluating them):

```python
UNIT = 'rustdesk.service'
STATE_DIR = Path('/var/lib/plproject/remote-support')
ENABLE_MARKER = STATE_DIR / 'enabled'
MAX_REQUEST_BYTES = 1024
ACCESS_DURATIONS = (900, 7200, 18000)
BOOT_ID_PATH = Path('/proc/sys/kernel/random/boot_id')
LOGGER = logging.getLogger('plproject.remote_support')
```

### `_elapsed_time`

```python
def _elapsed_time() -> float
```

### `_read_window`

```python
def _read_window() -> dict | None
```

### `_access_allowed`

```python
def _access_allowed() -> bool
```

### `_write_json`

```python
def _write_json(path: Path, value: dict) -> None
```

### `_expire_if_needed`

```python
def _expire_if_needed() -> None
```

### `_sync_state_directory`

```python
def _sync_state_directory() -> None
```

### `_systemctl`

```python
def _systemctl(*args: str) -> subprocess.CompletedProcess
```

### `_status`

```python
def _status() -> dict
```

### `_set_enabled`

```python
def _set_enabled(enabled: bool, duration_seconds: int=900) -> dict
```

### `handle_request`

```python
def handle_request(request: dict) -> dict
```

### `_serve_connection`

```python
def _serve_connection(connection: socket.socket) -> None
```

### `main`

```python
def main() -> None
```

## `password_client.py`

Source: [src/engine/remote_support/password_client.py](../../../src/engine/remote_support/password_client.py).

RustDesk password management without plaintext files or process arguments.

Imports (including optional/function-local imports; not a startup dependency list): `.session_client`.

### `RustDeskPasswordClient`

```python
class RustDeskPasswordClient(RustDeskSessionClient):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def get_password_status(self) -> dict
```

```python
def set_password(self, password: str) -> None
```

```python
def remove_password(self) -> None
```

## `session_client.py`

Source: [src/engine/remote_support/session_client.py](../../../src/engine/remote_support/session_client.py).

Read-only RustDesk 1.4.9 desktop-session query over its user IPC socket. VideoConnCount counts authenticated incoming desktop connections (not relay connections, pending authorization, or file transfers). The IPC API is internal; an incompatible RustDesk build must be reported as unknown, never as zero.

Imports (including optional/function-local imports; not a startup dependency list): `json`, `os`, `socket`, `time`.

### `RustDeskSessionClient`

```python
class RustDeskSessionClient:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, socket_path: str | None=None, timeout: float=1) -> None
```

```python
def get_session_count(self) -> int
```
