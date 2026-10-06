# Module reference: `src/applications/contour_matching_tester/model`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [contour_matching_tester_model.py](#contour_matching_tester_modelpy)

## `__init__.py`

Source: [src/applications/contour_matching_tester/model/__init__.py](../../../../src/applications/contour_matching_tester/model/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `contour_matching_tester_model.py`

Source: [src/applications/contour_matching_tester/model/contour_matching_tester_model.py](../../../../src/applications/contour_matching_tester/model/contour_matching_tester_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.applications.base.i_application_model`, `src.applications.contour_matching_tester.service.i_contour_matching_tester_service`, `typing`.

### `ContourMatchingTesterModel`

```python
class ContourMatchingTesterModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IContourMatchingTesterService)
```

```python
def load(self) -> None
```

```python
def save(self, *args, **kwargs) -> None
```

```python
def load_workpieces(self) -> list
```

```python
def capture(self) -> list
```

```python
def release_capture(self) -> None
```

```python
def select_workpiece(self, index: int) -> bool
```

```python
def run_matching(self, selected_index: int) -> Tuple[dict, int, List, List]
```

```python
def get_thumbnail(self, workpiece_index: int) -> Optional[bytes]
```

```python
@property
def is_captured(self) -> bool
```

```python
@property
def workpieces(self) -> list
```

```python
@property
def selected_index(self) -> Optional[int]
```

```python
@property
def captured_contours(self) -> list
```

```python
@property
def last_result(self) -> Optional[dict]
```
