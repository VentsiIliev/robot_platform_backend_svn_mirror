# Module reference: `src/robot_systems/paint/applications/paint_process_settings/controller`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [paint_process_settings_controller.py](#paint_process_settings_controllerpy)

## `paint_process_settings_controller.py`

Source: [src/robot_systems/paint/applications/paint_process_settings/controller/paint_process_settings_controller.py](../../../../../../src/robot_systems/paint/applications/paint_process_settings/controller/paint_process_settings_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `src.applications.base.background_worker`, `src.applications.base.i_application_controller`, `src.applications.base.styled_message_box`, `src.robot_systems.paint.applications.paint_process_settings.mapper`, `src.robot_systems.paint.applications.paint_process_settings.model.paint_process_settings_model`, `src.robot_systems.paint.applications.paint_process_settings.view.paint_process_settings_view`, `src.robot_systems.paint.processes.paint.configuration.models`, `src.robot_systems.paint.processes.paint.tray_dry.plate_layout`.

### `PaintProcessSettingsController`

```python
class PaintProcessSettingsController(IApplicationController, BackgroundWorker):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: PaintProcessSettingsModel, view: PaintProcessSettingsView)
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```
