# Module reference: `src/applications/intrinsic_calibration_capture/model`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [intrinsic_capture_model.py](#intrinsic_capture_modelpy)

## `__init__.py`

Source: [src/applications/intrinsic_calibration_capture/model/__init__.py](../../../../src/applications/intrinsic_calibration_capture/model/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `intrinsic_capture_model.py`

Source: [src/applications/intrinsic_calibration_capture/model/intrinsic_capture_model.py](../../../../src/applications/intrinsic_calibration_capture/model/intrinsic_capture_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `numpy`, `src.applications.base.i_application_model`, `src.applications.intrinsic_calibration_capture.service.i_intrinsic_capture_service`, `typing`.

### `IntrinsicCaptureModel`

```python
class IntrinsicCaptureModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IIntrinsicCaptureService)
```

```python
def load(self) -> None
```

```python
def save(self, *args, **kwargs) -> None
```

```python
def start_capture(self) -> None
```

```python
def stop_capture(self) -> None
```

```python
def is_running(self) -> bool
```

```python
def get_latest_frame(self) -> Optional[np.ndarray]
```

```python
def get_config(self) -> IntrinsicCaptureConfig
```

```python
def save_config(self, config: IntrinsicCaptureConfig) -> None
```
