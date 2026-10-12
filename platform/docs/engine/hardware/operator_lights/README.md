# Operator light outputs

`OperatorLights` writes named channels through `IRegisterTransport`, serializes
writes and exposes a cached snapshot of successful commands. That snapshot is
not physical lamp readback. Inactive outputs are cleared before active outputs
are set, so a partial I/O failure can leave a mixed indication.

`OperatorLightsConfig` validates distinct nonempty channel names, supported
transport selection, channel references and complete process-state mappings.
Missing or unknown process states are rejected while settings are constructed,
before hardware activation.

Retry, notifications and lifecycle ownership belong to the robot-system
coordinator. The tray-dryer coordinator retries the latest requested state with
bounded exponential backoff and owns transport closure on its writer thread.
See [tray-dryer recovery](../../../robot_systems/paint_tray_dry/RECOVERY.md) for
health semantics, notification localization and shutdown deadlines.
