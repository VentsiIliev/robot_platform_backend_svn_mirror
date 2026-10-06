# Module reference: `src/engine/hardware/generator/timer`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [generator_timer.py](#generator_timerpy)
- [i_generator_timer.py](#i_generator_timerpy)

## `__init__.py`

Source: [src/engine/hardware/generator/timer/__init__.py](../../../../../src/engine/hardware/generator/timer/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `generator_timer.py`

Source: [src/engine/hardware/generator/timer/generator_timer.py](../../../../../src/engine/hardware/generator/timer/generator_timer.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.engine.hardware.generator.timer.i_generator_timer`, `threading`, `time`, `typing`.

### `GeneratorTimer`

```python
class GeneratorTimer(IGeneratorTimer):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, timeout_minutes: float, on_timeout: Callable[[], None], poll_interval_s: float=5.0) -> None
```

```python
def start(self) -> None
```

```python
def stop(self) -> None
```

```python
@property
def elapsed_seconds(self) -> Optional[float]
```

### `NullGeneratorTimer`

```python
class NullGeneratorTimer(IGeneratorTimer):
```

No-op — use when timeout tracking is not needed.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def start(self) -> None
```

```python
def stop(self) -> None
```

```python
@property
def elapsed_seconds(self) -> Optional[float]
```

## `i_generator_timer.py`

Source: [src/engine/hardware/generator/timer/i_generator_timer.py](../../../../../src/engine/hardware/generator/timer/i_generator_timer.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `typing`.

### `IGeneratorTimer`

```python
class IGeneratorTimer(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def start(self) -> None
```

```python
@abstractmethod
def stop(self) -> None
```

```python
@property
@abstractmethod
def elapsed_seconds(self) -> Optional[float]
```
