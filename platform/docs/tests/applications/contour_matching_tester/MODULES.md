# Module reference: `tests/applications/contour_matching_tester`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_contour_matching_tester_model.py](#test_contour_matching_tester_modelpy)
- [test_contour_matching_tester_overlay.py](#test_contour_matching_tester_overlaypy)
- [test_contour_matching_tester_service.py](#test_contour_matching_tester_servicepy)

## `__init__.py`

Source: [tests/applications/contour_matching_tester/__init__.py](../../../../tests/applications/contour_matching_tester/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_contour_matching_tester_model.py`

Source: [tests/applications/contour_matching_tester/test_contour_matching_tester_model.py](../../../../tests/applications/contour_matching_tester/test_contour_matching_tester_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.contour_matching_tester.model.contour_matching_tester_model`, `unittest`, `unittest.mock`.

### `TestContourMatchingTesterModel`

```python
class TestContourMatchingTesterModel(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_matches_selected_workpiece_against_every_detected_contour(self)
```

```python
def test_reloading_workpieces_clears_selection(self)
```

```python
def test_clearing_selection_prevents_matching(self)
```

## `test_contour_matching_tester_overlay.py`

Source: [tests/applications/contour_matching_tester/test_contour_matching_tester_overlay.py](../../../../tests/applications/contour_matching_tester/test_contour_matching_tester_overlay.py).

Imports (including optional/function-local imports; not a startup dependency list): `numpy`, `src.applications.contour_matching_tester.controller.contour_matching_tester_controller`, `unittest`, `unittest.mock`.

### `TestContourMatchingTesterOverlay`

```python
class TestContourMatchingTesterOverlay(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_match_overlay_is_redrawn_on_later_camera_frames(self)
```

```python
def test_changing_workpiece_clears_match_overlay(self)
```

## `test_contour_matching_tester_service.py`

Source: [tests/applications/contour_matching_tester/test_contour_matching_tester_service.py](../../../../tests/applications/contour_matching_tester/test_contour_matching_tester_service.py).

Tests for contour_matching_tester service layer. Covers: - StubContourMatchingTesterService — interface compliance + behaviour - ContourMatchingTesterService — delegation + graceful fallback without optional services

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.contour_matching_tester.service.contour_matching_tester_service`, `src.applications.contour_matching_tester.service.stub_contour_matching_tester_service`, `src.robot_systems.paint.domain.workpieces.service.paint_workpiece_service`, `unittest`, `unittest.mock`.

### `_make_vision_service`

```python
def _make_vision_service()
```

### `_make_workpiece_service`

```python
def _make_workpiece_service(names=None)
```

### `TestStubContourMatchingTesterService`

```python
class TestStubContourMatchingTesterService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_get_workpieces_returns_list(self)
```

```python
def test_get_workpieces_returns_copy(self)
```

```python
def test_get_latest_contours_returns_list(self)
```

```python
def test_run_matching_returns_tuple(self)
```

```python
def test_get_thumbnail_returns_none(self)
```

### `TestContourMatchingTesterServiceGetWorkpieces`

```python
class TestContourMatchingTesterServiceGetWorkpieces(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_no_workpiece_service_returns_empty(self)
```

```python
def test_delegates_to_workpiece_service(self)
```

```python
def test_thumbnail_uses_workpiece_store_contract(self)
```

### `TestContourMatchingTesterServiceRunMatching`

```python
class TestContourMatchingTesterServiceRunMatching(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_paint_store_uses_same_matching_contract_as_glue(self)
```

```python
def test_no_vision_service_returns_empty_tuple(self)
```

```python
def test_delegates_to_vision_service(self)
```

### `TestContourMatchingTesterServiceWithoutVision`

```python
class TestContourMatchingTesterServiceWithoutVision(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_get_latest_contours_returns_empty(self)
```

```python
def test_run_matching_returns_empty_fallback(self)
```
