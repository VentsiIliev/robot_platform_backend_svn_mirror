# Paint process configuration

`models.py` defines process and projection settings, enum values, defaults, and cycle-local acceleration scaling. `serializer.py` owns JSON conversion and validation; `service.py` owns persisted settings access and live snapshots/listeners. The move preserves catalog keys, stored JSON, and runtime defaults.

[Module reference](MODULES.md).
