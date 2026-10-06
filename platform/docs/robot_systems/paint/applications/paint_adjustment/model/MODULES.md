# Module reference: `src/robot_systems/paint/applications/paint_adjustment/model`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [paint_adjustment_model.py](#paint_adjustment_modelpy)

## `__init__.py`

Source: [src/robot_systems/paint/applications/paint_adjustment/model/__init__.py](../../../../../../src/robot_systems/paint/applications/paint_adjustment/model/__init__.py).

Paint Adjustment model.

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `paint_adjustment_model.py`

Source: [src/robot_systems/paint/applications/paint_adjustment/model/paint_adjustment_model.py](../../../../../../src/robot_systems/paint/applications/paint_adjustment/model/paint_adjustment_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `..service.i_paint_adjustment_service`, `src.applications.base.i_application_model`.

### `PaintAdjustmentModel`

```python
class PaintAdjustmentModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IPaintAdjustmentService) -> None
```

```python
def load(self) -> str
```

```python
def is_paint_head_available(self) -> bool
```

```python
def get_preset_count(self) -> int
```

```python
def get_dial_config(self) -> PaintHeadDialConfig
```

```python
def read_current_position(self) -> int | None
```

```python
def start_single_paint_cycle(self) -> bool
```

```python
def get_paint_cycle_state(self) -> str
```

```python
def get_adjustment_options(self) -> PaintAdjustmentOptions
```

```python
def start_adjustment_cycle(self, options: PaintAdjustmentOptions) -> bool
```

```python
def paint_next_section(self, options: PaintAdjustmentOptions) -> bool
```

```python
def finish_adjustment_cycle(self) -> bool
```

```python
def get_adjustment_status(self) -> tuple[str, float, float]
```

```python
def adjust_paint(self, direction: str, degrees: int) -> int
```

```python
def adjust_paint_by_register_units(self, direction: str, units: int) -> PaintHeadCommandResult
```

```python
def go_to_setting(self, setting: int) -> PaintHeadCommandResult
```

```python
def go_to_position(self, position: int) -> PaintHeadCommandResult
```

```python
def save(self, *args, **kwargs) -> None
```

There is no persisted preview state.
