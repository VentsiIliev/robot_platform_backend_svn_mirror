# Module reference: `src/applications/robot_settings/controller`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [robot_settings_controller.py](#robot_settings_controllerpy)

## `__init__.py`

Source: [src/applications/robot_settings/controller/__init__.py](../../../../src/applications/robot_settings/controller/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `robot_settings_controller.py`

Source: [src/applications/robot_settings/controller/robot_settings_controller.py](../../../../src/applications/robot_settings/controller/robot_settings_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `logging`, `src.applications.base.background_worker`, `src.applications.base.i_application_controller`, `src.applications.base.styled_message_box`, `src.applications.robot_settings.model.mapper`, `src.applications.robot_settings.model.robot_settings_model`, `src.applications.robot_settings.view.movement_groups_tab`, `src.applications.robot_settings.view.robot_settings_view`, `src.engine.core.i_messaging_service`, `src.shared_contracts.declarations`, `src.shared_contracts.events.robot_events`, `threading`.

### `_MotionBridge`

```python
class _MotionBridge(QObject):
```

Declared fields/defaults:

```python
done = pyqtSignal(object, str)
failed = pyqtSignal(str, str)
```

### `_ConfigBridge`

```python
class _ConfigBridge(QObject):
```

Declared fields/defaults:

```python
changed = pyqtSignal()
```

### `RobotSettingsController`

```python
class RobotSettingsController(IApplicationController, BackgroundWorker):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: RobotSettingsModel, view: RobotSettingsView, messaging: IMessagingService)
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```
