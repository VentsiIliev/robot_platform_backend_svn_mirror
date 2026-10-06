# Module reference: `src/engine/hardware/generator/interfaces`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_generator_controller.py](#i_generator_controllerpy)
- [i_generator_transport.py](#i_generator_transportpy)

## `__init__.py`

Source: [src/engine/hardware/generator/interfaces/__init__.py](../../../../../src/engine/hardware/generator/interfaces/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `i_generator_controller.py`

Source: [src/engine/hardware/generator/interfaces/i_generator_controller.py](../../../../../src/engine/hardware/generator/interfaces/i_generator_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `src.engine.hardware.generator.models.generator_state`.

### `IGeneratorController`

```python
class IGeneratorController(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def turn_on(self) -> bool
```

Turn on the generator.

```python
@abstractmethod
def turn_off(self) -> bool
```

Turn off the generator.

```python
@abstractmethod
def get_state(self) -> GeneratorState
```

Get the current state of the generator.

## `i_generator_transport.py`

Source: [src/engine/hardware/generator/interfaces/i_generator_transport.py](../../../../../src/engine/hardware/generator/interfaces/i_generator_transport.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.communication.i_register_transport`.

### `IGeneratorTransport`

```python
class IGeneratorTransport(IRegisterTransport):
```

Semantic type alias — constrains injection sites to generator-specific transports. All registered I/O contracts are inherited from IRegisterTransport.
