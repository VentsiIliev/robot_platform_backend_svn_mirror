# Module reference: `src/applications/broker_debug/service`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [broker_debug_application_service.py](#broker_debug_application_servicepy)
- [i_broker_debug_service.py](#i_broker_debug_servicepy)
- [stub_broker_debug_service.py](#stub_broker_debug_servicepy)

## `__init__.py`

Source: [src/applications/broker_debug/service/__init__.py](../../../../src/applications/broker_debug/service/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `broker_debug_application_service.py`

Source: [src/applications/broker_debug/service/broker_debug_application_service.py](../../../../src/applications/broker_debug/service/broker_debug_application_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.applications.broker_debug.service.i_broker_debug_service`, `src.engine.core.i_messaging_service`, `typing`.

### `BrokerDebugApplicationService`

```python
class BrokerDebugApplicationService(IBrokerDebugService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, messaging: IMessagingService)
```

```python
def get_all_topics(self) -> List[str]
```

```python
def get_subscriber_count(self, topic: str) -> int
```

```python
def publish(self, topic: str, message: str) -> None
```

```python
def subscribe_spy(self, topic: str, callback: Callable) -> None
```

```python
def unsubscribe_spy(self, topic: str, callback: Callable) -> None
```

```python
def clear_topic(self, topic: str) -> None
```

```python
def get_topic_map(self) -> Dict[str, int]
```

## `i_broker_debug_service.py`

Source: [src/applications/broker_debug/service/i_broker_debug_service.py](../../../../src/applications/broker_debug/service/i_broker_debug_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `typing`.

### `IBrokerDebugService`

```python
class IBrokerDebugService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def get_all_topics(self) -> List[str]
```

```python
@abstractmethod
def get_subscriber_count(self, topic: str) -> int
```

```python
@abstractmethod
def publish(self, topic: str, message: str) -> None
```

```python
@abstractmethod
def subscribe_spy(self, topic: str, callback: Callable) -> None
```

```python
@abstractmethod
def unsubscribe_spy(self, topic: str, callback: Callable) -> None
```

```python
@abstractmethod
def clear_topic(self, topic: str) -> None
```

```python
@abstractmethod
def get_topic_map(self) -> Dict[str, int]
```

## `stub_broker_debug_service.py`

Source: [src/applications/broker_debug/service/stub_broker_debug_service.py](../../../../src/applications/broker_debug/service/stub_broker_debug_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.applications.broker_debug.service.i_broker_debug_service`, `typing`.

### `StubBrokerDebugService`

```python
class StubBrokerDebugService(IBrokerDebugService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def get_all_topics(self) -> List[str]
```

```python
def get_subscriber_count(self, topic: str) -> int
```

```python
def publish(self, topic: str, message: str) -> None
```

```python
def subscribe_spy(self, topic: str, callback: Callable) -> None
```

```python
def unsubscribe_spy(self, topic: str, callback: Callable) -> None
```

```python
def clear_topic(self, topic: str) -> None
```

```python
def get_topic_map(self) -> Dict[str, int]
```
