# Module reference: `src/applications/pick_and_place_visualizer`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [example_usage.py](#example_usagepy)
- [pick_and_place_visualizer_factory.py](#pick_and_place_visualizer_factorypy)

## `__init__.py`

Source: [src/applications/pick_and_place_visualizer/__init__.py](../../../src/applications/pick_and_place_visualizer/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.pick_and_place_visualizer.pick_and_place_visualizer_factory`, `src.applications.pick_and_place_visualizer.service.i_pick_and_place_visualizer_service`.

Package-level import/export surface:

```python
from src.applications.pick_and_place_visualizer.pick_and_place_visualizer_factory import PickAndPlaceVisualizerFactory
from src.applications.pick_and_place_visualizer.service.i_pick_and_place_visualizer_service import IPickAndPlaceVisualizerService
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `example_usage.py`

Source: [src/applications/pick_and_place_visualizer/example_usage.py](../../../src/applications/pick_and_place_visualizer/example_usage.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `src.applications.pick_and_place_visualizer.pick_and_place_visualizer_factory`, `src.applications.pick_and_place_visualizer.service.stub_pick_and_place_visualizer_service`, `sys`.

### `run_standalone`

```python
def run_standalone() -> None
```

## `pick_and_place_visualizer_factory.py`

Source: [src/applications/pick_and_place_visualizer/pick_and_place_visualizer_factory.py](../../../src/applications/pick_and_place_visualizer/pick_and_place_visualizer_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.applications.base.application_factory`, `src.applications.pick_and_place_visualizer.controller.pick_and_place_visualizer_controller`, `src.applications.pick_and_place_visualizer.model.pick_and_place_visualizer_model`, `src.applications.pick_and_place_visualizer.service.i_pick_and_place_visualizer_service`, `src.applications.pick_and_place_visualizer.view.pick_and_place_visualizer_view`, `src.engine.core.i_messaging_service`, `typing`.

### `PickAndPlaceVisualizerFactory`

```python
class PickAndPlaceVisualizerFactory:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def build(self, service: IPickAndPlaceVisualizerService, messaging: Optional[IMessagingService]=None, jog_service=None)
```
