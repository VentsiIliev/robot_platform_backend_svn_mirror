# Module reference: `src/engine/core`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [dependency_container.py](#dependency_containerpy)
- [i_coordinate_transformer.py](#i_coordinate_transformerpy)
- [i_health_checkable.py](#i_health_checkablepy)
- [i_messaging_service.py](#i_messaging_servicepy)
- [message_broker.py](#message_brokerpy)
- [messaging_service.py](#messaging_servicepy)

## `__init__.py`

Source: [src/engine/core/__init__.py](../../../src/engine/core/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `dependency_container.py`

Source: [src/engine/core/dependency_container.py](../../../src/engine/core/dependency_container.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `i_coordinate_transformer.py`

Source: [src/engine/core/i_coordinate_transformer.py](../../../src/engine/core/i_coordinate_transformer.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `typing`.

### `ICoordinateTransformer`

```python
class ICoordinateTransformer(ABC):
```

Transforms a 2D point from one coordinate space to another (canonical use: camera pixels → robot mm via homography).

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def transform(self, x: float, y: float) -> Tuple[float, float]
```

Return (x_out, y_out). Raises RuntimeError if not available.

```python
@abstractmethod
def is_available(self) -> bool
```

True if the transformation matrix is loaded and usable.

```python
@abstractmethod
def reload(self) -> bool
```

Re-read the matrix from its source. Returns True if the transformer is now available. Call this after a calibration run writes a new matrix file.

```python
@abstractmethod
def transform_to_tcp(self, x: float, y: float) -> Tuple[float, float]
```

Return (x_out, y_out) shifted by the camera-to-TCP offset. Raises RuntimeError if the matrix is not loaded or if no camera-to-TCP offset was provided at construction time.

```python
@abstractmethod
def inverse_transform(self, x: float, y: float) -> Tuple[float, float]
```

Return (x_out, y_out) in the source/image space. Raises RuntimeError if the inverse mapping is not available.

## `i_health_checkable.py`

Source: [src/engine/core/i_health_checkable.py](../../../src/engine/core/i_health_checkable.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`.

### `IHealthCheckable`

```python
class IHealthCheckable(ABC):
```

Optional interface for services that can report their own operational health. A service is healthy when it is connected and ready to accept commands. Implement this on any service that has a meaningful connected/ready state.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def is_healthy(self) -> bool
```

## `i_messaging_service.py`

Source: [src/engine/core/i_messaging_service.py](../../../src/engine/core/i_messaging_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `typing`.

### `IMessagingService`

```python
class IMessagingService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def subscribe(self, topic: str, callback: Callable) -> None
```

```python
@abstractmethod
def unsubscribe(self, topic: str, callback: Callable) -> None
```

```python
@abstractmethod
def publish(self, topic: str, message: Any) -> None
```

```python
@abstractmethod
def request(self, topic: str, message: Any, timeout: float=1.0) -> Any
```

```python
@abstractmethod
def get_subscriber_count(self, topic: str) -> int
```

```python
@abstractmethod
def get_all_topics(self) -> List[str]
```

```python
@abstractmethod
def clear_topic(self, topic: str) -> None
```

```python
@abstractmethod
def clear_all(self) -> None
```

## `message_broker.py`

Source: [src/engine/core/message_broker.py](../../../src/engine/core/message_broker.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.engine.core.i_messaging_service`, `traceback`, `typing`, `weakref`.

### `MessageBroker`

```python
class MessageBroker(IMessagingService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def subscribe(self, topic: str, callback: Callable)
```

```python
def unsubscribe(self, topic: str, callback: Callable)
```

```python
def publish(self, topic: str, message: Any)
```

```python
def get_subscriber_count(self, topic: str) -> int
```

```python
def get_all_topics(self) -> List[str]
```

```python
def clear_topic(self, topic: str)
```

```python
def request(self, topic: str, message: Any, timeout: float=1.0)
```

```python
def clear_all(self)
```

## `messaging_service.py`

Source: [src/engine/core/messaging_service.py](../../../src/engine/core/messaging_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.core.i_messaging_service`, `src.engine.core.message_broker`, `typing`.

### `MessagingService`

```python
class MessagingService(IMessagingService):
```

Concrete IMessagingService backed by MessageBroker. This is the only class outside engine/core that should be instantiated. MessageBroker is an implementation detail — it never leaks beyond this file. Swapping the underlying broker in future = replace this class only.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def subscribe(self, topic: str, callback: Callable) -> None
```

```python
def unsubscribe(self, topic: str, callback: Callable) -> None
```

```python
def publish(self, topic: str, message: Any) -> None
```

```python
def request(self, topic: str, message: Any, timeout: float=1.0) -> Any
```

```python
def get_subscriber_count(self, topic: str) -> int
```

```python
def get_all_topics(self) -> List[str]
```

```python
def clear_topic(self, topic: str) -> None
```

```python
def clear_all(self) -> None
```
