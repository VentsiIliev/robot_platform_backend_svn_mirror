# Module reference: `src/applications/network_settings/model`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [network_settings_model.py](#network_settings_modelpy)

## `__init__.py`

Source: [src/applications/network_settings/model/__init__.py](../../../../src/applications/network_settings/model/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `network_settings_model.py`

Source: [src/applications/network_settings/model/network_settings_model.py](../../../../src/applications/network_settings/model/network_settings_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.i_application_model`, `src.applications.network_settings.service.i_network_settings_service`.

### `NetworkSettingsModel`

```python
class NetworkSettingsModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: INetworkSettingsService) -> None
```

```python
def load(self) -> None
```

The controller schedules network discovery after the page is shown.

```python
def save(self, target: str, settings: dict) -> None
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
def get_remote_support_status(self) -> dict
```

```python
def set_remote_support_enabled(self, enabled: bool) -> dict
```
