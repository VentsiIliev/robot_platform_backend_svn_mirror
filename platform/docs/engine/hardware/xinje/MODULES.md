# Module reference: `src/engine/hardware/xinje`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [ma_io_address_map.py](#ma_io_address_mappy)

## `__init__.py`

Source: [src/engine/hardware/xinje/__init__.py](../../../../src/engine/hardware/xinje/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.xinje.ma_io_address_map`.

Package-level import/export surface:

```python
from src.engine.hardware.xinje.ma_io_address_map import XinjeMA8X8YR, XinjeMAIOAddressMap
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['XinjeMA8X8YR', 'XinjeMAIOAddressMap']
```

## `ma_io_address_map.py`

Source: [src/engine/hardware/xinje/ma_io_address_map.py](../../../../src/engine/hardware/xinje/ma_io_address_map.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
XinjeMA8X8YR = XinjeMAIOAddressMap(model='MA-8X8YR', input_addresses={f'X{index}': index for index in range(8)}, output_addresses={f'Y{index}': 128 + index for index in range(8)})
```

### `XinjeMAIOAddressMap`

```python
@dataclass(frozen=True)
class XinjeMAIOAddressMap:
```

Modbus address map for Xinje MA digital I/O modules.

Declared fields/defaults:

```python
model: str
input_addresses: Mapping[str, int]
output_addresses: Mapping[str, int]
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def resolve_input(self, point: int | str) -> int
```

```python
def resolve_output(self, point: int | str) -> int
```
