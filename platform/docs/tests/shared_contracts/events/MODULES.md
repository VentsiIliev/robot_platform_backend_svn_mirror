# Module reference: `tests/shared_contracts/events`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [test_event_contracts.py](#test_event_contractspy)

## `test_event_contracts.py`

Source: [tests/shared_contracts/events/test_event_contracts.py](../../../../tests/shared_contracts/events/test_event_contracts.py).

Imports (including optional/function-local imports; not a startup dependency list): `datetime`, `src.shared_contracts.events.glue_process_events`, `src.shared_contracts.events.localization_events`, `src.shared_contracts.events.notification_events`, `src.shared_contracts.events.pick_and_place_events`, `src.shared_contracts.events.process_events`, `src.shared_contracts.events.weight_events`, `unittest`.

### `TestProcessEvents`

```python
class TestProcessEvents(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_process_topics_are_stable(self)
```

```python
def test_process_state_event_uses_utc_timestamp(self)
```

```python
def test_process_support_events_preserve_payload(self)
```

### `TestPickAndPlaceEvents`

```python
class TestPickAndPlaceEvents(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_pick_and_place_topics_are_stable(self)
```

```python
def test_pick_and_place_events_preserve_payload(self)
```

### `TestWeightEvents`

```python
class TestWeightEvents(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_weight_topics_are_stable(self)
```

```python
def test_weight_reading_validity_uses_inclusive_bounds(self)
```

```python
def test_cell_state_event_uses_utc_timestamp(self)
```

### `TestUiEvents`

```python
class TestUiEvents(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_localization_topic_and_event_are_stable(self)
```

```python
def test_notification_event_defaults_are_independent(self)
```
