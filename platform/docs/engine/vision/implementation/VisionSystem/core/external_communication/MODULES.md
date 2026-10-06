# Module reference: `src/engine/vision/implementation/VisionSystem/core/external_communication`

[Package guide](README.md) · [Complete source index](../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [system_state_management.py](#system_state_managementpy)

## `__init__.py`

Source: [src/engine/vision/implementation/VisionSystem/core/external_communication/__init__.py](../../../../../../../src/engine/vision/implementation/VisionSystem/core/external_communication/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `system_state_management.py`

Source: [src/engine/vision/implementation/VisionSystem/core/external_communication/system_state_management.py](../../../../../../../src/engine/vision/implementation/VisionSystem/core/external_communication/system_state_management.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `enum`, `logging`, `src.shared_contracts.events.vision_events`, `threading`.

### `SubscriptionManager`

```python
class SubscriptionManager:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, vision_system, messaging_service)
```

```python
def subscribe_to_threshold_update(self)
```

```python
def subscribe_to_auto_brightness_toggle(self)
```

```python
def subscribe_all(self)
```

### `MessagePublisher`

```python
class MessagePublisher:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, messaging_service)
```

```python
def publish_latest_image(self, image)
```

```python
def publish_camera_frame(self, image)
```

```python
def publish_calibration_image_captured(self, calibration_images)
```

```python
def publish_thresh_image(self, thresh_image)
```

```python
def publish_state(self, state)
```

```python
def publish_calibration_feedback(self, feedback)
```

### `ServiceState`

```python
class ServiceState(Enum):
```

Declared fields/defaults:

```python
UNKNOWN = 0
INITIALIZING = 1
IDLE = 2
STARTED = 3
PAUSED = 4
STOPPED = 5
ERROR = 6
```

### `ServiceStateMessage`

```python
@dataclass
class ServiceStateMessage:
```

Declared fields/defaults:

```python
id: str
state: ServiceState
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def to_dict(self)
```

### `StateManager`

```python
class StateManager:
```

Used inside individual services. Publishes service state changes.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service_id: str, initial_state: ServiceState, message_publisher)
```

```python
def update_state(self, new_state: ServiceState)
```
