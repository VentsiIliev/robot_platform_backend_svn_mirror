# Module reference: `src/applications/device_control/model`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [device_control_model.py](#device_control_modelpy)

## `device_control_model.py`

Source: [src/applications/device_control/model/device_control_model.py](../../../../src/applications/device_control/model/device_control_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.applications.base.i_application_model`, `src.applications.device_control.service.i_device_control_service`, `typing`.

### `DeviceControlModel`

```python
class DeviceControlModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IDeviceControlService) -> None
```

```python
def load(self) -> None
```

```python
def save(self, *args, **kwargs) -> None
```

```python
def get_devices(self) -> List[IDeviceControlDevice]
```

```python
def execute_device_action(self, device_key: str, action: str) -> bool
```

```python
def read_device_state(self, device_key: str) -> Mapping[str, object]
```

```python
def set_device_enabled(self, device_key: str, enabled: bool) -> bool
```

```python
def is_device_enabled(self, device_key: str) -> bool
```

```python
def get_motors(self) -> List[MotorEntry]
```

```python
def get_motor_health_snapshot(self) -> Dict[int, bool]
```

```python
def is_laser_available(self) -> bool
```

```python
def is_vacuum_pump_available(self) -> bool
```

```python
def is_motor_available(self) -> bool
```

```python
def is_generator_available(self) -> bool
```

```python
def laser_on(self) -> None
```

```python
def laser_off(self) -> None
```

```python
def vacuum_pump_on(self) -> bool
```

```python
def vacuum_pump_off(self) -> bool
```

```python
def motor_on(self, address: int) -> bool
```

```python
def motor_off(self, address: int) -> bool
```

```python
def generator_on(self) -> bool
```

```python
def generator_off(self) -> bool
```
