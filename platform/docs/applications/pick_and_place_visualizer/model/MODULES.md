# Module reference: `src/applications/pick_and_place_visualizer/model`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [pick_and_place_visualizer_model.py](#pick_and_place_visualizer_modelpy)

## `__init__.py`

Source: [src/applications/pick_and_place_visualizer/model/__init__.py](../../../../src/applications/pick_and_place_visualizer/model/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `pick_and_place_visualizer_model.py`

Source: [src/applications/pick_and_place_visualizer/model/pick_and_place_visualizer_model.py](../../../../src/applications/pick_and_place_visualizer/model/pick_and_place_visualizer_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.i_application_model`, `src.applications.pick_and_place_visualizer.service.i_pick_and_place_visualizer_service`.

### `PickAndPlaceVisualizerModel`

```python
class PickAndPlaceVisualizerModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IPickAndPlaceVisualizerService)
```

```python
def load(self)
```

```python
def save(self, *args, **kwargs) -> None
```

```python
def run_simulation(self) -> SimResult
```

```python
def get_plane_bounds(self)
```

```python
def set_simulation(self, value: bool) -> None
```

```python
def get_process_state(self) -> str
```

```python
def set_step_mode(self, value: bool) -> None
```

```python
def is_step_mode_enabled(self) -> bool
```

```python
def step_process(self) -> None
```

```python
def start_process(self) -> None
```

```python
def stop_process(self) -> None
```

```python
def pause_process(self) -> None
```

```python
def reset_process(self) -> None
```
