# Module reference: `src/engine/hardware/generator`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [explore.py](#explorepy)
- [generator_controller.py](#generator_controllerpy)
- [mock_runner.py](#mock_runnerpy)

## `__init__.py`

Source: [src/engine/hardware/generator/__init__.py](../../../../src/engine/hardware/generator/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.generator.generator_controller`, `src.engine.hardware.generator.interfaces.i_generator_controller`, `src.engine.hardware.generator.interfaces.i_generator_transport`, `src.engine.hardware.generator.models.generator_config`, `src.engine.hardware.generator.models.generator_state`, `src.engine.hardware.generator.timer.generator_timer`, `src.engine.hardware.generator.timer.i_generator_timer`.

Package-level import/export surface:

```python
from src.engine.hardware.generator.interfaces.i_generator_controller import IGeneratorController
from src.engine.hardware.generator.interfaces.i_generator_transport import IGeneratorTransport
from src.engine.hardware.generator.models.generator_config import GeneratorConfig
from src.engine.hardware.generator.models.generator_state import GeneratorState
from src.engine.hardware.generator.timer.i_generator_timer import IGeneratorTimer
from src.engine.hardware.generator.timer.generator_timer import GeneratorTimer, NullGeneratorTimer
from src.engine.hardware.generator.generator_controller import GeneratorController
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['IGeneratorController', 'IGeneratorTransport', 'GeneratorConfig', 'GeneratorState', 'IGeneratorTimer', 'GeneratorTimer', 'NullGeneratorTimer', 'GeneratorController']
```

## `explore.py`

Source: [src/engine/hardware/generator/explore.py](../../../../src/engine/hardware/generator/explore.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `generator_controller.py`

Source: [src/engine/hardware/generator/generator_controller.py](../../../../src/engine/hardware/generator/generator_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.engine.hardware.generator.interfaces.i_generator_controller`, `src.engine.hardware.generator.interfaces.i_generator_transport`, `src.engine.hardware.generator.models.generator_config`, `src.engine.hardware.generator.models.generator_state`, `src.engine.hardware.generator.timer.generator_timer`, `src.engine.hardware.generator.timer.i_generator_timer`.

### `GeneratorController`

```python
class GeneratorController(IGeneratorController):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, transport: IGeneratorTransport, config: GeneratorConfig=None, timer: IGeneratorTimer=None) -> None
```

```python
def turn_on(self) -> bool
```

```python
def turn_off(self) -> bool
```

```python
def get_state(self) -> GeneratorState
```

## `mock_runner.py`

Source: [src/engine/hardware/generator/mock_runner.py](../../../../src/engine/hardware/generator/mock_runner.py).

Generator controller mock runner — manual integration / smoke test. Run with: python src/engine/hardware/generator/mock_runner.y_pixels No serial port required. MockGeneratorTransport intercepts all register I/O and prints what would be sent over the wire. Use it to verify GeneratorController logic, timer behaviour, and error handling without any hardware attached.

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.engine.hardware.generator.generator_controller`, `src.engine.hardware.generator.interfaces.i_generator_transport`, `src.engine.hardware.generator.models.generator_config`, `src.engine.hardware.generator.models.generator_state`, `src.engine.hardware.generator.timer.generator_timer`, `sys`, `time`.

### `MockGeneratorTransport`

```python
class MockGeneratorTransport(IGeneratorTransport):
```

In-memory transport. All register writes are recorded; reads return values from a configurable register bank. Attributes: register_bank – dict[address → int] returned by reads raise_on_write – if True, write_register raises IOError raise_on_read – if True, read_register raises IOError call_log – list of (method, address, value) for assertions

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

```python
def read_register(self, address: int) -> int
```

```python
def write_register(self, address: int, value: int) -> None
```

```python
def set_on(self) -> None
```

Configure: state register reports generator ON (hardware: 0 = ON).

```python
def set_off(self) -> None
```

Configure: state register reports generator OFF (hardware: 1 = OFF).

```python
def reset(self) -> None
```

### `_section`

```python
def _section(title: str) -> None
```

### `_make_controller`

```python
def _make_controller(transport: MockGeneratorTransport, timeout_cb=None, timeout_minutes: float=0.0) -> GeneratorController
```

### `scenario_turn_on_off`

```python
def scenario_turn_on_off(t: MockGeneratorTransport) -> None
```

Basic turn_on / get_state / turn_off sequence.

### `scenario_get_state_on_and_off`

```python
def scenario_get_state_on_and_off(t: MockGeneratorTransport) -> None
```

Verify state register decoding for both ON and OFF.

### `scenario_timeout`

```python
def scenario_timeout(t: MockGeneratorTransport) -> None
```

Verify timer fires on_timeout after configured duration.

### `scenario_elapsed_time`

```python
def scenario_elapsed_time(t: MockGeneratorTransport) -> None
```

Verify elapsed_seconds increments while running.

### `scenario_transport_failure`

```python
def scenario_transport_failure(t: MockGeneratorTransport) -> None
```

Verify controller returns False and records comm error on failure.
