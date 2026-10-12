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
