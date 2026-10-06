# Module reference: `tests/applications/broker_debug`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_broker_debug_service.py](#test_broker_debug_servicepy)

## `__init__.py`

Source: [tests/applications/broker_debug/__init__.py](../../../../tests/applications/broker_debug/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_broker_debug_service.py`

Source: [tests/applications/broker_debug/test_broker_debug_service.py](../../../../tests/applications/broker_debug/test_broker_debug_service.py).

Tests for broker_debug service layer. Covers: - StubBrokerDebugService — interface compliance + in-memory behaviour - BrokerDebugApplicationService — delegation to IMessagingService

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.broker_debug.service.broker_debug_application_service`, `src.applications.broker_debug.service.i_broker_debug_service`, `src.applications.broker_debug.service.stub_broker_debug_service`, `unittest`, `unittest.mock`.

### `_make_messaging`

```python
def _make_messaging(topics=None)
```

### `TestStubBrokerDebugService`

```python
class TestStubBrokerDebugService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_get_all_topics_returns_list(self)
```

```python
def test_get_all_topics_returns_sorted_list(self)
```

```python
def test_get_subscriber_count_returns_int(self)
```

```python
def test_get_subscriber_count_unknown_topic_returns_zero(self)
```

```python
def test_publish_does_not_mutate_topic_map(self)
```

```python
def test_subscribe_spy_does_not_mutate_topic_map(self)
```

```python
def test_unsubscribe_spy_does_not_mutate_topic_map(self)
```

```python
def test_clear_topic_removes_topic(self)
```

```python
def test_clear_unknown_topic_leaves_topic_map_unchanged(self)
```

```python
def test_get_topic_map_returns_dict(self)
```

```python
def test_get_topic_map_values_are_ints(self)
```

### `TestBrokerDebugApplicationServiceTopics`

```python
class TestBrokerDebugApplicationServiceTopics(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_get_all_topics_delegates_to_messaging(self)
```

```python
def test_get_subscriber_count_delegates_to_messaging(self)
```

### `TestBrokerDebugApplicationServicePublish`

```python
class TestBrokerDebugApplicationServicePublish(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_publish_delegates_to_messaging(self)
```

### `TestBrokerDebugApplicationServiceSpy`

```python
class TestBrokerDebugApplicationServiceSpy(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_subscribe_spy_calls_messaging_subscribe(self)
```

```python
def test_unsubscribe_spy_calls_messaging_unsubscribe(self)
```

```python
def test_subscribe_spy_stores_callback(self)
```

```python
def test_unsubscribe_spy_removes_stored_callback(self)
```

### `TestBrokerDebugApplicationServiceTopicMap`

```python
class TestBrokerDebugApplicationServiceTopicMap(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_get_topic_map_counts_subscribers_per_topic(self)
```

```python
def test_get_topic_map_returns_dict(self)
```
