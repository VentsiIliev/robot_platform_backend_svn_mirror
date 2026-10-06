# Module reference: `src/applications/network_settings/service`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_network_settings_service.py](#i_network_settings_servicepy)
- [network_backend.py](#network_backendpy)
- [network_settings_service.py](#network_settings_servicepy)
- [remote_support_client.py](#remote_support_clientpy)
- [stub_network_settings_service.py](#stub_network_settings_servicepy)

## `__init__.py`

Source: [src/applications/network_settings/service/__init__.py](../../../../src/applications/network_settings/service/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `i_network_settings_service.py`

Source: [src/applications/network_settings/service/i_network_settings_service.py](../../../../src/applications/network_settings/service/i_network_settings_service.py).

Platform-independent contract for the shared Network Settings application.

Imports (including optional/function-local imports; not a startup dependency list): `abc`.

### `INetworkSettingsService`

```python
class INetworkSettingsService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def scan_wifi(self) -> list[dict]
```

```python
@abstractmethod
def list_wired(self) -> list[dict]
```

```python
@abstractmethod
def connect_wifi(self, ssid: str, password: str, secure: bool) -> None
```

```python
@abstractmethod
def disconnect_wifi(self) -> None
```

```python
@abstractmethod
def forget_wifi(self, ssid: str) -> None
```

```python
@abstractmethod
def connect_wired(self, device: str) -> None
```

```python
@abstractmethod
def disconnect_wired(self, device: str) -> None
```

```python
@abstractmethod
def get_wifi_ipv4(self) -> dict
```

```python
@abstractmethod
def get_wired_ipv4(self, device: dict) -> dict
```

```python
@abstractmethod
def apply_ipv4(self, target: str, settings: dict) -> None
```

```python
@abstractmethod
def get_remote_support_status(self) -> dict
```

```python
@abstractmethod
def set_remote_support_enabled(self, enabled: bool) -> dict
```

## `network_backend.py`

Source: [src/applications/network_settings/service/network_backend.py](../../../../src/applications/network_settings/service/network_backend.py).

OS network adapters extracted from the standalone network manager. No Qt dependencies belong in this module; it runs behind the shared service.

Imports (including optional/function-local imports; not a startup dependency list): `html`, `ipaddress`, `os`, `re`, `subprocess`, `sys`, `tempfile`.

### `run_command`

```python
def run_command(command)
```

### `prefix_to_netmask`

```python
def prefix_to_netmask(prefix)
```

### `netmask_to_prefix`

```python
def netmask_to_prefix(mask)
```

### `split_nmcli`

```python
def split_nmcli(line)
```

Split nmcli terse output while respecting escaped ':' characters.

### `LinuxBackend`

```python
class LinuxBackend:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def scan_wifi(self)
```

```python
def connect_wifi(self, ssid, password=None)
```

```python
def disconnect_wifi(self)
```

```python
def get_devices(self)
```

```python
def get_wired(self)
```

```python
def get_connection_settings(self, connection)
```

```python
def apply_settings(self, connection, settings)
```

```python
def disconnect_device(self, device)
```

```python
def connect_device(self, device)
```

```python
def forget_wifi(self, ssid)
```

### `WindowsBackend`

```python
class WindowsBackend:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def scan_wifi(self)
```

```python
def current_wifi_ssid(self)
```

```python
def connect_wifi(self, ssid, password=None, secure=True)
```

```python
def create_wifi_profile(self, ssid, password, secure)
```

```python
def disconnect_wifi(self)
```

```python
def get_interfaces(self)
```

```python
def get_wired(self)
```

```python
def get_connection_settings(self, interface)
```

```python
def apply_settings(self, interface, settings)
```

```python
def disconnect_device(self, interface)
```

```python
def connect_device(self, interface)
```

```python
def forget_wifi(self, ssid)
```

## `network_settings_service.py`

Source: [src/applications/network_settings/service/network_settings_service.py](../../../../src/applications/network_settings/service/network_settings_service.py).

OS command adapter for network settings. No Qt code runs in this layer.

Imports (including optional/function-local imports; not a startup dependency list): `.i_network_settings_service`, `.network_backend`, `.remote_support_client`, `ipaddress`, `re`, `sys`.

### `NetworkSettingsService`

```python
class NetworkSettingsService(INetworkSettingsService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, backend=None, platform: str | None=None, remote_support_client=None) -> None
```

```python
def scan_wifi(self) -> list[dict]
```

```python
def list_wired(self) -> list[dict]
```

```python
def connect_wifi(self, ssid: str, password: str, secure: bool) -> None
```

```python
def disconnect_wifi(self) -> None
```

```python
def forget_wifi(self, ssid: str) -> None
```

```python
def connect_wired(self, device: str) -> None
```

```python
def disconnect_wired(self, device: str) -> None
```

```python
def get_wifi_ipv4(self) -> dict
```

```python
def get_wired_ipv4(self, device: dict) -> dict
```

```python
def apply_ipv4(self, target: str, settings: dict) -> None
```

```python
def get_remote_support_status(self) -> dict
```

```python
def set_remote_support_enabled(self, enabled: bool) -> dict
```

## `remote_support_client.py`

Source: [src/applications/network_settings/service/remote_support_client.py](../../../../src/applications/network_settings/service/remote_support_client.py).

Compatibility import for the shared remote-support socket client.

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.remote_support.client`.

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['RemoteSupportClient']
```

## `stub_network_settings_service.py`

Source: [src/applications/network_settings/service/stub_network_settings_service.py](../../../../src/applications/network_settings/service/stub_network_settings_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `.i_network_settings_service`.

### `StubNetworkSettingsService`

```python
class StubNetworkSettingsService(INetworkSettingsService):
```

In-memory adapter for standalone previews and application tests.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

```python
def scan_wifi(self) -> list[dict]
```

```python
def list_wired(self) -> list[dict]
```

```python
def connect_wifi(self, ssid: str, password: str, secure: bool) -> None
```

```python
def disconnect_wifi(self) -> None
```

```python
def forget_wifi(self, ssid: str) -> None
```

```python
def connect_wired(self, device: str) -> None
```

```python
def disconnect_wired(self, device: str) -> None
```

```python
def get_wifi_ipv4(self) -> dict
```

```python
def get_wired_ipv4(self, device: dict) -> dict
```

```python
def apply_ipv4(self, target: str, settings: dict) -> None
```

```python
def get_remote_support_status(self) -> dict
```

```python
def set_remote_support_enabled(self, enabled: bool) -> dict
```
