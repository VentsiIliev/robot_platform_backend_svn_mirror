# EtherCAT Diagnostics

A shared MVC screen for a master/slave diagnostic snapshot and optional error reset. The application depends on `IEthercatDiagnosticsService`; it does not own an EtherCAT master or discover hardware itself.

`EthercatDiagnosticsSnapshot` carries master state/message, slave records and raw diagnostic fields. Each `EthercatSlaveStatus` can contain identity, state, online/operational status, error, statusword and details. Unknown/absent fields are represented explicitly rather than treated as a healthy master.

The controller refreshes on load and on explicit request using the shared `BackgroundWorker`, sets the view busy while work runs, and pushes either a snapshot or an error message. Reset is enabled only when the provider reports support; reset completion displays its result and refreshes again. `stop()` stops tracked worker threads. The default interface implementation reports reset unsupported.

The runtime service adapts the injected robot/backend diagnostics. The stub is available for isolated tests. Registration in a robot system's `application_wiring.py` determines availability; the existence of this package does not automatically expose it in every shell. See [tests](../../tests/applications/ethercat_diagnostics/README.md) for service/controller coverage.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `controller/` | [controller](controller/README.md) |
| `model/` | [model](model/README.md) |
| `service/` | [service](service/README.md) |
| `view/` | [view](view/README.md) |

[Complete source index](../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
