# Module reference: `src/engine/hardware/generator/models`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [generator_config.py](#generator_configpy)
- [generator_state.py](#generator_statepy)

## `__init__.py`

Source: [src/engine/hardware/generator/models/__init__.py](../../../../../src/engine/hardware/generator/models/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `generator_config.py`

Source: [src/engine/hardware/generator/models/generator_config.py](../../../../../src/engine/hardware/generator/models/generator_config.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`.

### `GeneratorConfig`

```python
@dataclass
class GeneratorConfig:
```

Declared fields/defaults:

```python
relay_register: int = 9
state_register: int = 10
timeout_minutes: float = 5.0
```

## `generator_state.py`

Source: [src/engine/hardware/generator/models/generator_state.py](../../../../../src/engine/hardware/generator/models/generator_state.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `typing`.

### `GeneratorState`

```python
@dataclass
class GeneratorState:
```

Declared fields/defaults:

```python
is_on: bool = False
is_healthy: bool = False
communication_errors: List[str] = field(default_factory=list)
elapsed_seconds: Optional[float] = None
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def has_errors(self) -> bool
```
