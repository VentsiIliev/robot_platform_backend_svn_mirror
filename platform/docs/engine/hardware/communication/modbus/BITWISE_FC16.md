# Bitwise FC16 transport

`modbus_bitwise_fc16` exposes logical bit addresses 0..15 within one readable
holding register. `bitwise_register` on the slave entry selects that register
(default 1). Reads use FC3. Binary writes read the current word, preserve unrelated
bits and write the resulting word using FC16. No coil operation is used.

```json
"slaves": {
  "default": {
    "slave_address": 10,
    "profile_name": "default",
    "transport_type": "modbus_bitwise_fc16",
    "bitwise_register": 1
  }
}
```

For two light channels, outputs are bit indices rather than register addresses:

```json
"outputs": {"light_9": 9, "light_10": 10},
"commands": {"on": 1, "off": 0}
```

The light-service channel names must match these output names. Its enabled flag
and transport selection also need to select real hardware. This transport does
not add a Device Control tab or change the process-state channel mapping.

Selecting this transport changes the contract for all peripherals resolved through
that slave entry: numeric addresses now mean bits and writes accept only 0/1.
Do not switch an existing mixed register-based slave without remapping binary
outputs and separating consumers requiring ordinary word registers. In particular,
a paint-head position register must retain the ordinary register transport.
The paint-head service supports an explicit peripheral override:

```json
"paint_head": {
  "enabled": true,
  "slave_id": 10,
  "transport_type": "modbus_register_fc16",
  "outputs": {"position": 2}
}
```

Keep the existing paint-head `commands` and calibration fields alongside this
selection. Its readback and range checks are unchanged. The slave-wide default
can remain `modbus_bitwise_fc16`. Both transports share the same physical serial
bus lock and connection settings. The Device Control enable toggle preserves the
override. This override is currently consumed by the paint-head service; other
peripheral builders continue to use the slave default.
Current numeric-slave lookup selects one configured entry; duplicate aliases with
the same numeric ID do not automatically select different transports per peripheral.

The hardware must return the actual output word when register 1 is read. Serial
bus locks serialize the full read–modify–write sequence within this process,
including separate transport instances. They cannot protect against another
application or an external master writing concurrently. An ordinary full-word
write to the same register can still overwrite previously set bits.

Tests cover bit preservation, FC16 use, ranges/values, batch operations, configured
register selection and concurrent transport instances. Real hardware acceptance
has not been performed.

## Vacuum pump and blow-off

A legacy pump mapping using holding register 1 with ON mask 1 and blow-off mask
4 maps to pump bit 0 and blow-off bit 2. With `modbus_bitwise_fc16`, configure:

```json
"outputs": {"pump": "0", "blow_off": "2"},
"commands": {"on": 1, "off": 0, "blow_off_on": 1, "blow_off_off": 0}
```

The slave's `bitwise_register` selects physical holding register 1. These output
addresses select bits inside that word; they are not holding-register addresses.
The pulse updates only bit 2 and preserves the other output bits. Pump and
blow-off must use distinct bit indices in 0..15 and binary command values.
The vacuum-pump factory rejects incompatible bitwise mappings before creating
its transport. Ordinary word-register transports retain their existing contract.
Restart the application after changing these startup-built controller settings.
For external machine data, update the active profile's persisted peripherals
file as well as any factory defaults intended for future installations.
