# Module reference: `src/applications/calibration`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [calibration_factory.py](#calibration_factorypy)
- [example_usage.py](#example_usagepy)

## `__init__.py`

Source: [src/applications/calibration/__init__.py](../../../src/applications/calibration/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.calibration.calibration_factory`, `src.applications.calibration.service.i_calibration_service`.

Package-level import/export surface:

```python
from src.applications.calibration.calibration_factory import CalibrationFactory
from src.applications.calibration.service.i_calibration_service import ICalibrationService
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `calibration_factory.py`

Source: [src/applications/calibration/calibration_factory.py](../../../src/applications/calibration/calibration_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.application_factory`, `src.applications.base.i_application_controller`, `src.applications.base.i_application_model`, `src.applications.base.i_application_view`, `src.applications.calibration.controller.calibration_controller`, `src.applications.calibration.model.calibration_model`, `src.applications.calibration.service.i_calibration_service`, `src.applications.calibration.view.calibration_view`, `src.shared_contracts.declarations`.

### `CalibrationFactory`

```python
class CalibrationFactory(ApplicationFactory):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, work_area_definitions: list[WorkAreaDefinition] | None=None, *, show_laser_tab: bool=True, show_height_mapping_tab: bool=True)
```

```python
def build(self, service, messaging=None, jog_service=None)
```

## `example_usage.py`

Source: [src/applications/calibration/example_usage.py](../../../src/applications/calibration/example_usage.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `cv2`, `logging`, `numpy`, `src.applications.calibration.calibration_factory`, `src.applications.calibration.service.stub_calibration_service`, `src.engine.core.messaging_service`, `src.shared_contracts.events.vision_events`, `sys`, `threading`, `time`.

### `_publish_fake_frames`

```python
def _publish_fake_frames(messaging: MessagingService, stop: threading.Event) -> None
```

### `run_standalone`

```python
def run_standalone()
```
