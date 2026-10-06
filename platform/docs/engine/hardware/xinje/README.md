# `src/engine/hardware/xinje/` — Xinje Address Maps

Modbus address maps for Xinje digital I/O modules. Pure data and resolution logic
— no I/O, no Qt, no settings dependency.

---

## Files

| File | Contents |
|------|----------|
| `ma_io_address_map.py` | `XinjeMAIOAddressMap`, `XinjeMA8X8YR` |

---

## `XinjeMAIOAddressMap`

```python
@dataclass(frozen=True)
class XinjeMAIOAddressMap:
    model: str
    input_addresses: Mapping[str, int]
    output_addresses: Mapping[str, int]

    def resolve_input(self, point: int | str) -> int: ...
    def resolve_output(self, point: int | str) -> int: ...
```

### Resolution rules

`_resolve()` is shared by both methods and accepts either a raw integer or a
symbolic name:

| Input | Behaviour |
|-------|-----------|
| `int` | Returned unchanged — an escape hatch for addressing outside the map |
| `"Y5"`, `"y5"` | Looked up in `output_addresses`; `.strip().upper()` is applied first |
| `"0x80"` | Parsed with `int(key, 0)`, so hex/decimal/octal prefixes all work |
| Unknown name | Raises `ValueError` listing every valid point for that model and direction |

Case-insensitivity and the `int(key, 0)` fallback together mean configuration can
be written either as `"Y5"` or `"133"` and still resolve correctly.

---

## `XinjeMA8X8YR`

```python
XinjeMA8X8YR = XinjeMAIOAddressMap(
    model="MA-8X8YR",
    input_addresses={f"X{index}": index for index in range(8)},          # X0..X7  → 0..7
    output_addresses={f"Y{index}": 128 + index for index in range(8)},   # Y0..Y7  → 128..135
)
```

The output base of `128` matches `_MA_OUTPUT_START` in
`XinjeMA8X8YRTransport`, which owns the `K128`–`K143` FC15 write window. The
symbolic map stops at `Y7` → `135`, but the transport maintains a 16-bit shadow
covering the full `128`–`143` window, so the extra relays remain addressable by
raw integer.

---

## Consumers

Engine code resolves symbolic point names through this map at construction time,
so the register numbers never appear in application or settings code:

| Consumer | Call |
|----------|------|
| `ModbusLaserControl` | `resolve_output(register)` — default `"Y5"` |
| `ModbusFanControl` | `resolve_output(register)` |
| `VacuumPumpController` | `resolve_output(config.pump_register)` and `resolve_output(config.blow_off_register)` |
| `VacuumSensorService` | Chooses direction from the point name — `resolve_input` when `sensor_register` starts with `X`, otherwise `resolve_output` |
| `ModbusPhysicalControlButtons` | `resolve_input` for each configured input, `resolve_output` for each output |

`ModbusVacuumPumpTransport` subclasses `XinjeMA8X8YRTransport` directly rather
than using the address map, because it inherits the whole coil-write protocol.

---

## Design Notes

- **Frozen dataclass** — address maps are immutable module-level constants, safe
  to share across threads without locking.
- **Symbolic names are a settings concern.** Devices accept `int | str` and
  resolve immediately, so a settings file may store either form.
- **Adding a model** means adding one more `XinjeMAIOAddressMap` instance; no
  class changes are required.
