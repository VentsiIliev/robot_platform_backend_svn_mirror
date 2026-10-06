# Module reference: `src/applications/shaft_alignment/model`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [shaft_alignment_model.py](#shaft_alignment_modelpy)

## `__init__.py`

Source: [src/applications/shaft_alignment/model/__init__.py](../../../../src/applications/shaft_alignment/model/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.shaft_alignment.model.shaft_alignment_model`.

Package-level import/export surface:

```python
from src.applications.shaft_alignment.model.shaft_alignment_model import ShaftAlignmentModel
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ShaftAlignmentModel']
```

## `shaft_alignment_model.py`

Source: [src/applications/shaft_alignment/model/shaft_alignment_model.py](../../../../src/applications/shaft_alignment/model/shaft_alignment_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.base.i_application_model`, `src.applications.shaft_alignment.service.i_shaft_alignment_service`, `src.applications.shaft_alignment.settings.shaft_alignment_settings`.

### `ShaftAlignmentModel`

```python
class ShaftAlignmentModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IShaftAlignmentService) -> None
```

```python
def load(self) -> tuple[AlignmentSnapshot, ShaftAlignmentSettings]
```

```python
def save(self, settings: ShaftAlignmentSettings, **kwargs) -> None
```

```python
def get_settings(self) -> ShaftAlignmentSettings
```

```python
def start(self) -> None
```

```python
def stop_detection(self) -> None
```

```python
def refresh(self) -> AlignmentSnapshot
```

```python
def capture_reference(self, sample_count: int) -> None
```

```python
def set_thresholds(self, thresholds: AlignmentThresholds) -> None
```

```python
def close(self) -> None
```

```python
def check_alignment(self) -> bool
```
