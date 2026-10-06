# Module reference: `tests/engine/hardware/generator`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_generator_config.py](#test_generator_configpy)
- [test_generator_controller.py](#test_generator_controllerpy)
- [test_generator_state.py](#test_generator_statepy)
- [test_generator_timer.py](#test_generator_timerpy)
- [test_null_generator_timer.py](#test_null_generator_timerpy)

## `__init__.py`

Source: [tests/engine/hardware/generator/__init__.py](../../../../../tests/engine/hardware/generator/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_generator_config.py`

Source: [tests/engine/hardware/generator/test_generator_config.py](../../../../../tests/engine/hardware/generator/test_generator_config.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.generator.models.generator_config`, `unittest`.

### `TestGeneratorConfigDefaults`

```python
class TestGeneratorConfigDefaults(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_default_relay_register(self)
```

```python
def test_default_state_register(self)
```

```python
def test_default_timeout_minutes(self)
```

### `TestGeneratorConfigCustomValues`

```python
class TestGeneratorConfigCustomValues(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_relay_register_set(self)
```

```python
def test_state_register_set(self)
```

```python
def test_timeout_minutes_set(self)
```

## `test_generator_controller.py`

Source: [tests/engine/hardware/generator/test_generator_controller.py](../../../../../tests/engine/hardware/generator/test_generator_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.generator.generator_controller`, `src.engine.hardware.generator.models.generator_config`, `src.engine.hardware.generator.models.generator_state`, `src.engine.hardware.generator.timer.generator_timer`, `unittest`, `unittest.mock`.

### `_transport`

```python
def _transport()
```

### `_config`

```python
def _config()
```

### `_timer`

```python
def _timer()
```

### `_make`

```python
def _make(transport=None, config=None, timer=None)
```

### `TestGeneratorControllerTurnOn`

```python
class TestGeneratorControllerTurnOn(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_turn_on_writes_1_to_relay_register(self)
```

```python
def test_turn_on_starts_timer(self)
```

```python
def test_turn_on_returns_true_on_success(self)
```

```python
def test_turn_on_returns_false_when_transport_raises(self)
```

```python
def test_turn_on_does_not_start_timer_when_transport_raises(self)
```

### `TestGeneratorControllerTurnOff`

```python
class TestGeneratorControllerTurnOff(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_turn_off_writes_0_to_relay_register(self)
```

```python
def test_turn_off_stops_timer(self)
```

```python
def test_turn_off_returns_true_on_success(self)
```

```python
def test_turn_off_returns_false_when_transport_raises(self)
```

```python
def test_turn_off_does_not_stop_timer_when_transport_raises(self)
```

### `TestGeneratorControllerGetState`

```python
class TestGeneratorControllerGetState(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_get_state_reads_state_register(self)
```

```python
def test_raw_0_means_is_on_true(self)
```

```python
def test_raw_1_means_is_on_false(self)
```

```python
def test_get_state_returns_healthy_true_on_success(self)
```

```python
def test_get_state_returns_no_errors_on_success(self)
```

```python
def test_get_state_includes_elapsed_from_timer(self)
```

```python
def test_get_state_returns_unhealthy_when_transport_raises(self)
```

```python
def test_get_state_returns_is_on_false_when_transport_raises(self)
```

```python
def test_get_state_includes_error_message_when_transport_raises(self)
```

```python
def test_get_state_still_includes_elapsed_when_transport_raises(self)
```

```python
def test_returns_generator_state_instance(self)
```

### `TestGeneratorControllerUsesCustomConfig`

```python
class TestGeneratorControllerUsesCustomConfig(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_uses_custom_relay_register(self)
```

```python
def test_uses_custom_state_register(self)
```

### `TestGeneratorControllerDefaults`

```python
class TestGeneratorControllerDefaults(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_default_config_is_used_when_none_provided(self)
```

```python
def test_default_timer_is_null_timer(self)
```

## `test_generator_state.py`

Source: [tests/engine/hardware/generator/test_generator_state.py](../../../../../tests/engine/hardware/generator/test_generator_state.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.generator.models.generator_state`, `unittest`.

### `TestGeneratorStateDefaults`

```python
class TestGeneratorStateDefaults(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_is_on_default_false(self)
```

```python
def test_is_healthy_default_false(self)
```

```python
def test_communication_errors_default_empty(self)
```

```python
def test_elapsed_seconds_default_none(self)
```

```python
def test_has_errors_false_when_no_errors(self)
```

### `TestGeneratorStateHasErrors`

```python
class TestGeneratorStateHasErrors(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_has_errors_true_when_errors_present(self)
```

```python
def test_has_errors_false_when_list_empty(self)
```

### `TestGeneratorStateStr`

```python
class TestGeneratorStateStr(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_str_on_healthy(self)
```

```python
def test_str_off_unhealthy(self)
```

```python
def test_str_includes_elapsed_when_set(self)
```

```python
def test_str_excludes_elapsed_when_none(self)
```

### `TestGeneratorStateImmutableErrors`

```python
class TestGeneratorStateImmutableErrors(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_separate_instances_have_independent_error_lists(self)
```

## `test_generator_timer.py`

Source: [tests/engine/hardware/generator/test_generator_timer.py](../../../../../tests/engine/hardware/generator/test_generator_timer.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.generator.timer.generator_timer`, `threading`, `time`, `unittest`.

### `TestGeneratorTimerElapsed`

```python
class TestGeneratorTimerElapsed(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_elapsed_none_before_start(self)
```

```python
def test_elapsed_non_none_after_start(self)
```

```python
def test_elapsed_positive_after_start(self)
```

```python
def test_elapsed_frozen_after_stop(self)
```

### `TestGeneratorTimerStop`

```python
class TestGeneratorTimerStop(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_stop_without_start_records_stop_time_without_thread(self)
```

```python
def test_double_start_does_not_create_extra_threads(self)
```

### `TestGeneratorTimerTimeout`

```python
class TestGeneratorTimerTimeout(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_on_timeout_called_when_timeout_reached(self)
```

```python
def test_on_timeout_not_called_when_stopped_early(self)
```

## `test_null_generator_timer.py`

Source: [tests/engine/hardware/generator/test_null_generator_timer.py](../../../../../tests/engine/hardware/generator/test_null_generator_timer.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.generator.timer.generator_timer`, `unittest`.

### `TestNullGeneratorTimer`

```python
class TestNullGeneratorTimer(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_elapsed_seconds_is_none(self)
```

```python
def test_start_preserves_none_elapsed_seconds(self)
```

```python
def test_stop_preserves_none_elapsed_seconds(self)
```

```python
def test_elapsed_seconds_still_none_after_start(self)
```

```python
def test_elapsed_seconds_still_none_after_stop(self)
```
