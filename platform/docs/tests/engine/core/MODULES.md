# Module reference: `tests/engine/core`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [test_message_broker.py](#test_message_brokerpy)

## `test_message_broker.py`

Source: [tests/engine/core/test_message_broker.py](../../../../tests/engine/core/test_message_broker.py).

Imports (including optional/function-local imports; not a startup dependency list): `gc`, `src.engine.core.message_broker`, `src.engine.core.messaging_service`, `unittest`.

### `_Recorder`

```python
class _Recorder:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def on_message(self, message)
```

### `_SelfUnsubscriber`

```python
class _SelfUnsubscriber:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, broker, topic)
```

```python
def on_message(self, message)
```

### `TestMessageBroker`

```python
class TestMessageBroker(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def tearDown(self)
```

```python
def test_publish_delivers_to_bound_subscriber(self)
```

```python
def test_unsubscribe_removes_bound_subscriber(self)
```

```python
def test_publish_allows_callback_to_unsubscribe_itself(self)
```

```python
def test_dead_bound_method_is_cleaned_up(self)
```

```python
def test_request_returns_first_non_none_response(self)
```

```python
def test_get_all_topics_includes_published_topic_without_subscribers(self)
```

### `TestMessagingService`

```python
class TestMessagingService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def tearDown(self)
```

```python
def test_publish_and_subscribe_use_shared_broker(self)
```
