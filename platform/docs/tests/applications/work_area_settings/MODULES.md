# Module reference: `tests/applications/work_area_settings`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [test_work_area_settings_view.py](#test_work_area_settings_viewpy)

## `test_work_area_settings_view.py`

Source: [tests/applications/work_area_settings/test_work_area_settings_view.py](../../../../tests/applications/work_area_settings/test_work_area_settings_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `numpy`, `os`, `src.applications.work_area_settings.controller.work_area_settings_controller`, `src.applications.work_area_settings.view.work_area_settings_view`, `src.shared_contracts.declarations`, `unittest`, `unittest.mock`.

### `WorkAreaSettingsViewTests`

```python
class WorkAreaSettingsViewTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls) -> None
```

```python
def setUp(self) -> None
```

```python
def tearDown(self) -> None
```

```python
def test_corner_nudge_uses_frame_pixels_and_reset_restores_saved_roi(self) -> None
```

```python
def test_roi_role_and_zoom_controls_use_shared_camera_view(self) -> None
```

```python
def test_step_buttons_do_not_overlap_the_direction_pad(self) -> None
```

### `WorkAreaSettingsControllerTests`

```python
class WorkAreaSettingsControllerTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_vision_state_event_uses_state_value(self) -> None
```

```python
def test_saved_roi_becomes_reset_baseline_only_after_success(self) -> None
```
