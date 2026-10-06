# Module reference: `src/applications/aruco_z_probe`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [aruco_z_probe_factory.py](#aruco_z_probe_factorypy)
- [example_usage.py](#example_usagepy)

## `__init__.py`

Source: [src/applications/aruco_z_probe/__init__.py](../../../src/applications/aruco_z_probe/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `aruco_z_probe_factory.py`

Source: [src/applications/aruco_z_probe/aruco_z_probe_factory.py](../../../src/applications/aruco_z_probe/aruco_z_probe_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.aruco_z_probe.controller.aruco_z_probe_controller`, `src.applications.aruco_z_probe.model.aruco_z_probe_model`, `src.applications.aruco_z_probe.service.i_aruco_z_probe_service`, `src.applications.aruco_z_probe.view.aruco_z_probe_view`, `src.applications.base.application_factory`.

### `ArucoZProbeFactory`

```python
class ArucoZProbeFactory(ApplicationFactory):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def build(self, service, messaging=None, jog_service=None)
```

## `example_usage.py`

Source: [src/applications/aruco_z_probe/example_usage.py](../../../src/applications/aruco_z_probe/example_usage.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `src.applications.aruco_z_probe.aruco_z_probe_factory`, `src.applications.aruco_z_probe.service.stub_aruco_z_probe_service`, `sys`.

### `run_standalone`

```python
def run_standalone() -> None
```
