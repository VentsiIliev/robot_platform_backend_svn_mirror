# Module reference: `src/applications/glue_cell_settings/model`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [glue_cell_settings_model.py](#glue_cell_settings_modelpy)
- [mapper.py](#mapperpy)

## `__init__.py`

Source: [src/applications/glue_cell_settings/model/__init__.py](../../../../src/applications/glue_cell_settings/model/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `glue_cell_settings_model.py`

Source: [src/applications/glue_cell_settings/model/glue_cell_settings_model.py](../../../../src/applications/glue_cell_settings/model/glue_cell_settings_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.applications.base.i_application_model`, `src.applications.glue_cell_settings.model.mapper`, `src.applications.glue_cell_settings.service.i_glue_cell_settings_service`, `src.engine.hardware.weight.config`, `typing`.

### `GlueCellSettingsModel`

```python
class GlueCellSettingsModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IGlueCellSettingsService)
```

```python
def load(self) -> CellsConfig
```

```python
def save(self, cell_id: int, flat: Dict) -> None
```

```python
def tare(self, cell_id: int) -> bool
```

```python
def get_cell_flat(self, cell_id: int) -> Optional[Dict]
```

```python
def get_cell_ids(self)
```

## `mapper.py`

Source: [src/applications/glue_cell_settings/model/mapper.py](../../../../src/applications/glue_cell_settings/model/mapper.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `src.engine.hardware.weight.config`, `typing`.

### `GlueCellMapper`

```python
class GlueCellMapper:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@staticmethod
def cell_to_flat(cell: CellConfig) -> Dict
```

```python
@staticmethod
def flat_to_cell(flat: Dict, original: CellConfig) -> CellConfig
```
