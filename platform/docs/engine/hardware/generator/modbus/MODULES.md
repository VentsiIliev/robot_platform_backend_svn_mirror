# Module reference: `src/engine/hardware/generator/modbus`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [modbus_generator_factory.py](#modbus_generator_factorypy)
- [modbus_generator_transport.py](#modbus_generator_transportpy)

## `__init__.py`

Source: [src/engine/hardware/generator/modbus/__init__.py](../../../../../src/engine/hardware/generator/modbus/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `modbus_generator_factory.py`

Source: [src/engine/hardware/generator/modbus/modbus_generator_factory.py](../../../../../src/engine/hardware/generator/modbus/modbus_generator_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.hardware.communication.modbus.modbus`, `src.engine.hardware.generator.generator_controller`, `src.engine.hardware.generator.interfaces.i_generator_controller`, `src.engine.hardware.generator.modbus.modbus_generator_transport`, `src.engine.hardware.generator.models.generator_config`, `src.engine.hardware.generator.timer.generator_timer`, `src.engine.hardware.generator.timer.i_generator_timer`, `typing`.

### `build_modbus_generator_controller`

```python
def build_modbus_generator_controller(modbus_config: ModbusConfig, generator_config: GeneratorConfig=None, on_timeout: Optional[Callable[[], None]]=None) -> IGeneratorController
```

## `modbus_generator_transport.py`

Source: [src/engine/hardware/generator/modbus/modbus_generator_transport.py](../../../../../src/engine/hardware/generator/modbus/modbus_generator_transport.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.communication.modbus.modbus_register_transport`, `src.engine.hardware.generator.interfaces.i_generator_transport`.

### `ModbusGeneratorTransport`

```python
class ModbusGeneratorTransport(ModbusRegisterTransport, IGeneratorTransport):
```

Modbus RTU transport for generator relay boards.
