# EtherCAT network mode notes

The active ZeroErr launch path uses the robot package's EtherCAT startup helpers
and machine-specific master/NIC configuration. See the
[build/launch guide](BUILD_SCRIPTS_README.md),
[EtherCAT log](eRob_moveit/src/eRob_ROS2_MoveIt/zeroerr/docs/ETHERCAT_ZEROERR_COMMUNICATION.md)
and [RT policy](eRob_moveit/zeroerr_rt_policy.env).

## Local helper from the original workstation

Earlier operator notes used `net_mode ethercat`, `net_mode normal` and
`net_mode status`. **`net_mode` is not supplied by this repository.** Its behavior
and privilege requirements must be checked on the host before using it. The
recorded NIC names were `enp3s0` (EtherCAT) and `wlp0s20f3` (Wi-Fi); they are not
portable configuration defaults.

Switching a control NIC or stopping its master interrupts hardware communication.
Do network reconfiguration with the robot stopped and the control stack shut down,
following the deployed host's master/NIC setup. A dedicated EtherCAT NIC and a
separate IP-network interface avoid competing traffic.

## Read-only checks

```bash
ip -br link
nmcli device status
ethercat master
ethercat slaves
```

Compare the discovered slave count and OP state with the configured six-drive
ZeroErr setup. Monitor lost frames and measured controller timing; do not infer
loop frequency or physical stopping performance solely from a master snapshot.
The production controller/observer cycle is configured by the robot stack (the
current sensorless controller is designed for 2 kHz), not by these notes' earlier
1000 Hz examples.

For the RT loop's readiness, timing and overrun telemetry, see the
[sensorless runbook](eRob_moveit/src/eRob_ROS2_MoveIt/zeroerr/collision_detection/docs/SENSORLESS_COLLISION_DETECTION.md).
