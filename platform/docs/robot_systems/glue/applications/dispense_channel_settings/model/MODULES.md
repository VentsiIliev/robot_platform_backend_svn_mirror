# Module reference: `src/robot_systems/glue/applications/dispense_channel_settings/model`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [dispense_channel_settings_model.py](#dispense_channel_settings_modelpy)

## `dispense_channel_settings_model.py`

Source: [src/robot_systems/glue/applications/dispense_channel_settings/model/dispense_channel_settings_model.py](../../../../../../src/robot_systems/glue/applications/dispense_channel_settings/model/dispense_channel_settings_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.applications.base.i_application_model`, `src.robot_systems.glue.applications.dispense_channel_settings.service.i_dispense_channel_settings_service`, `src.shared_contracts.declarations`, `typing`.

### `DispenseChannelSettingsModel`

```python
class DispenseChannelSettingsModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IDispenseChannelSettingsService)
```

```python
def load(self) -> List[DispenseChannelDefinition]
```

```python
def get_channel_flat(self, channel_id: str) -> Optional[Dict]
```

```python
def get_glue_type_choices(self) -> List[str]
```

```python
def save(self, channel_id: str, flat: Dict) -> None
```

```python
def tare(self, channel_id: str) -> bool
```

```python
def start_pump_test(self, channel_id: str) -> bool
```

```python
def stop_pump_test(self, channel_id: str) -> bool
```

```python
def get_channel_for_cell_id(self, cell_id: int) -> Optional[str]
```
