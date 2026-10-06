# Module reference: `tests/engine/process`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_base_process.py](#test_base_processpy)
- [test_executable_state_machine.py](#test_executable_state_machinepy)
- [test_process_sequence.py](#test_process_sequencepy)

## `__init__.py`

Source: [tests/engine/process/__init__.py](../../../../tests/engine/process/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_base_process.py`

Source: [tests/engine/process/test_base_process.py](../../../../tests/engine/process/test_base_process.py).

Tests for src/engine/process/base_process.y_pixels BaseProcess is the abstract base for all robot processes. Covers state transitions, broker publishing, hook invocation, and service requirement enforcement.

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.process.base_process`, `src.engine.process.process_requirements`, `src.shared_contracts.events.process_events`, `unittest`, `unittest.mock`.

### `_ms`

```python
def _ms()
```

### `_ConcreteProcess`

```python
class _ConcreteProcess(BaseProcess):
```

Minimal concrete subclass with tracked hook calls.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, **kwargs)
```

### `_make`

```python
def _make(messaging=None, **kwargs) -> _ConcreteProcess
```

### `TestBaseProcessInitialState`

```python
class TestBaseProcessInitialState(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_initial_state_is_idle(self)
```

```python
def test_process_id_stored(self)
```

### `TestBaseProcessStateTransitions`

```python
class TestBaseProcessStateTransitions(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_start_from_idle_transitions_to_running(self)
```

```python
def test_stop_from_running_transitions_to_stopped(self)
```

```python
def test_stop_from_running_publishes_message_when_provided(self)
```

```python
def test_pause_from_running_transitions_to_paused(self)
```

```python
def test_resume_from_paused_transitions_to_running(self)
```

```python
def test_start_from_stopped_transitions_to_running(self)
```

```python
def test_stop_from_idle_is_no_op(self)
```

```python
def test_pause_from_idle_is_no_op(self)
```

```python
def test_set_error_from_running(self)
```

```python
def test_set_error_from_idle(self)
```

```python
def test_reset_errors_returns_to_idle(self)
```

### `TestBaseProcessHooks`

```python
class TestBaseProcessHooks(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_on_start_called_on_start(self)
```

```python
def test_on_stop_called_on_stop(self)
```

```python
def test_on_pause_called_on_pause(self)
```

```python
def test_on_resume_called_on_resume_from_paused(self)
```

```python
def test_on_start_not_called_from_idle_stop(self)
```

```python
def test_hook_exception_forces_error_state(self)
```

### `TestBaseProcessBrokerPublishing`

```python
class TestBaseProcessBrokerPublishing(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_state_published_on_start(self)
```

```python
def test_active_topic_published_on_start(self)
```

```python
def test_state_published_on_stop(self)
```

### `TestBaseProcessRequirements`

```python
class TestBaseProcessRequirements(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_requirements_block_start_when_service_unavailable(self)
```

```python
def test_requirements_allow_start_when_service_available(self)
```

## `test_executable_state_machine.py`

Source: [tests/engine/process/test_executable_state_machine.py](../../../../tests/engine/process/test_executable_state_machine.py).

Tests for src/engine/process/executable_state_machine.y_pixels Covers stop_execution, loop exit, on_enter/on_exit callbacks, broker publishing, and exception handling inside handlers.

Imports (including optional/function-local imports; not a startup dependency list): `enum`, `src.engine.process.executable_state_machine`, `threading`, `time`, `unittest`, `unittest.mock`.

### `_StopEvent`

```python
class _StopEvent:
```

Minimal stand-in for threading.Event used as context.stop_event.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def set(self)
```

```python
def is_set(self)
```

```python
def clear(self)
```

### `_FakeContext`

```python
class _FakeContext:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

### `S`

```python
class S(Enum):
```

Declared fields/defaults:

```python
A = auto()
B = auto()
DONE = auto()
ERROR = auto()
```

### `_build_simple`

```python
def _build_simple(context=None, handler_a=None, handler_b=None, broker=None) -> ExecutableStateMachine
```

Two-state machine: A → B → DONE.

### `TestExecutableStateMachineStop`

```python
class TestExecutableStateMachineStop(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_stop_sets_running_false(self)
```

```python
def test_stop_sets_context_stop_event(self)
```

```python
def test_stop_without_context_still_clears_running_flag(self)
```

```python
def test_stop_without_stop_event_attribute_still_clears_running_flag(self)
```

### `TestExecutableStateMachineExecution`

```python
class TestExecutableStateMachineExecution(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_step_executes_single_transition_without_resetting(self)
```

```python
def test_step_records_timing_in_snapshot(self)
```

```python
def test_reset_restores_initial_state_and_clears_snapshot(self)
```

```python
def test_simple_run_visits_all_states(self)
```

```python
def test_loop_exits_when_running_set_false(self)
```

Handler sets stop flag; loop must exit within timeout.

```python
def test_invalid_transition_exits_loop(self)
```

Handler returns a state not in transition rules → loop must exit.

```python
def test_unhandled_exception_in_handler_exits_loop(self)
```

```python
def test_missing_handler_exits_loop(self)
```

No handler registered for initial state → loop exits cleanly.

```python
def test_step_records_invalid_transition_error(self)
```

```python
def test_get_snapshot_returns_machine_state_details(self)
```

### `TestExecutableStateMachineCallbacks`

```python
class TestExecutableStateMachineCallbacks(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_on_enter_called_before_handler(self)
```

```python
def test_on_exit_called_after_handler(self)
```

### `TestExecutableStateMachineBroker`

```python
class TestExecutableStateMachineBroker(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_state_published_to_broker_on_each_state(self)
```

### `TestExecutableStateMachineBuilder`

```python
class TestExecutableStateMachineBuilder(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_build_raises_without_registry(self)
```

```python
def test_build_raises_without_initial_state(self)
```

```python
def test_build_returns_machine(self)
```

## `test_process_sequence.py`

Source: [tests/engine/process/test_process_sequence.py](../../../../tests/engine/process/test_process_sequence.py).

Tests for src/engine/process/process_sequence.y_pixels ProcessSequence orchestrates a list of IProcess instances in order, auto-advancing to the next process when the current one stops. Covered: - Init: empty list raises ValueError - start(): fresh start, subscribe to first process, set _current - start(): resume from PAUSED — no re-subscribe, no index reset - stop(): delegate to current, unsubscribe, safe when no active - pause(): delegate to current, safe when no active - reset_errors(): delegate, clear _current, unsubscribe, safe when no active - _on_current_stopped chain: STOPPED → advance, subscribe next, start next - _on_current_stopped: non-STOPPED events are ignored - _on_current_stopped on last process: _current cleared, index reset - Full three-process chain end-to-end

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.process.process_sequence`, `src.shared_contracts.events.process_events`, `unittest`, `unittest.mock`.

### `_make_proc`

```python
def _make_proc(pid: str, state: ProcessState=ProcessState.IDLE)
```

### `_ms`

```python
def _ms()
```

### `_stopped`

```python
def _stopped(pid: str) -> ProcessStateEvent
```

### `_running`

```python
def _running(pid: str) -> ProcessStateEvent
```

### `_get_callback`

```python
def _get_callback(ms, topic)
```

Return the callback registered for *topic* (last one wins).

### `TestProcessSequenceInit`

```python
class TestProcessSequenceInit(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_empty_list_raises_value_error(self)
```

```python
def test_single_process_accepted(self)
```

```python
def test_initial_current_is_none(self)
```

```python
def test_initial_index_is_zero(self)
```

### `TestProcessSequenceFreshStart`

```python
class TestProcessSequenceFreshStart(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_start_calls_first_process_start(self)
```

```python
def test_start_sets_current_to_first_process(self)
```

```python
def test_start_sets_index_to_zero(self)
```

```python
def test_start_subscribes_to_first_process_state_topic(self)
```

```python
def test_restart_after_completion_resets_to_first_process(self)
```

### `TestProcessSequenceResume`

```python
class TestProcessSequenceResume(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_start_when_current_paused_calls_process_start(self)
```

```python
def test_start_when_current_paused_does_not_re_subscribe(self)
```

```python
def test_start_when_current_paused_does_not_change_current(self)
```

### `TestProcessSequenceStop`

```python
class TestProcessSequenceStop(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_stop_calls_current_process_stop(self)
```

```python
def test_stop_unsubscribes_from_current_topic(self)
```

```python
def test_stop_when_no_active_does_not_call_process_or_unsubscribe(self)
```

### `TestProcessSequencePause`

```python
class TestProcessSequencePause(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_pause_calls_current_process_pause(self)
```

```python
def test_pause_when_no_active_does_not_call_process_pause(self)
```

### `TestProcessSequenceResetErrors`

```python
class TestProcessSequenceResetErrors(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_reset_errors_calls_current_process_reset_errors(self)
```

```python
def test_reset_errors_clears_current(self)
```

```python
def test_reset_errors_resets_index_to_zero(self)
```

```python
def test_reset_errors_unsubscribes_from_current_topic(self)
```

```python
def test_reset_errors_when_no_active_preserves_idle_sequence_state(self)
```

### `TestProcessSequenceChaining`

```python
class TestProcessSequenceChaining(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_stopped_event_advances_current_to_next(self)
```

```python
def test_stopped_event_increments_index(self)
```

```python
def test_stopped_event_starts_next_process(self)
```

```python
def test_stopped_event_subscribes_to_next_topic(self)
```

```python
def test_stopped_event_unsubscribes_from_completed_topic(self)
```

```python
def test_non_stopped_events_do_not_advance(self)
```

```python
def test_last_process_stopped_clears_current(self)
```

```python
def test_last_process_stopped_resets_index_to_zero(self)
```

```python
def test_last_process_stopped_does_not_start_anything(self)
```

```python
def test_full_three_process_sequence(self)
```

### `TestProcessSequenceTransitionHook`

```python
class TestProcessSequenceTransitionHook(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_before_next_start_hook_runs_before_starting_next_process(self)
```

```python
def test_before_next_start_hook_false_blocks_next_process_start(self)
```

```python
def test_before_next_start_hook_exception_blocks_next_process_start(self)
```
