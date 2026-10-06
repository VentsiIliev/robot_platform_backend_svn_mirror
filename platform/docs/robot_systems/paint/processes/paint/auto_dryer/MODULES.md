# Module reference: `src/robot_systems/paint/processes/paint/auto_dryer`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [dryer_release_coordinator.py](#dryer_release_coordinatorpy)

## `__init__.py`

Source: [src/robot_systems/paint/processes/paint/auto_dryer/__init__.py](../../../../../../src/robot_systems/paint/processes/paint/auto_dryer/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `dryer_release_coordinator.py`

Source: [src/robot_systems/paint/processes/paint/auto_dryer/dryer_release_coordinator.py](../../../../../../src/robot_systems/paint/processes/paint/auto_dryer/dryer_release_coordinator.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `concurrent.futures`, `logging`, `threading`, `time`.

### `DryerReleaseCoordinator`

```python
class DryerReleaseCoordinator:
```

Run post-release dryer commands serially without blocking paint production.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, dryer, *, status_timeout_s: float=10.0, status_poll_interval_s: float=0.1, eject_confirmation_delay_s: float=1.0, next_position_confirmation_delay_s: float=0.3) -> None
```

```python
def on_workpiece_release_verified(self) -> bool
```

Queue next-position → eject processing and return immediately.

```python
def shutdown(self) -> None
```

```python
def wait_until_ready_for_release(self) -> tuple[bool, str]
```

Wait for the previous sequence so another dropoff cannot overfill the dryer.
