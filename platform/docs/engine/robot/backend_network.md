# Backend network configuration

`config/backend_network.json` is the source of truth for the platform/backend transport endpoints. It contains:

| Field | Meaning |
|---|---|
| `bind_host` | IP address used by REST and all three backend WebSocket listeners |
| `client_host` | Backend IP address used by platform clients and startup probes |
| `http_port` | REST command/status port |
| `state_ws_port` | `/ws/state` port |
| `execution_ws_port` | `/ws/execution` port |
| `sensor_ws_port` | `/ws/sensors` port |

The shipped file uses loopback (`127.0.0.1`) and ports 5000–5003. A wildcard bind address is allowed only as an explicit configuration choice; `client_host` cannot be a wildcard. IP addresses and four distinct integer ports in 1–65535 are required. Missing files, malformed JSON, missing/unknown keys, and invalid values stop configuration loading. They do not fall back to other addresses.

The platform defaults, calibration client, startup probes and backend monitor consume this file. REST and WebSocket listeners receive the same values through the backend config loader. Robot/profile YAML no longer defines endpoint addresses or ports. The `REST_WS_*_ENABLED` switches remain robot settings.

## File location and deployment

Source runs use `platform/config/backend_network.json`. The platform launcher passes its absolute path to the backend through `ROBOT_BACKEND_NETWORK_CONFIG`. That environment variable selects the file only; it does not override individual values.

Packaged platform builds include the file under `_internal/config/`. The launcher passes that bundled path to the installed backend. For an installation-owned file that survives application upgrades, set the same absolute `ROBOT_BACKEND_NETWORK_CONFIG` path for the platform and any separately launched backend. A backend started from this source checkout can locate the sibling platform file; standalone installed backends must receive the absolute path explicitly.

Restart the platform and backend after editing the file. These are startup settings, not live network reconfiguration. Rebuild/reinstall `erob_moveit_runtime` after taking the code change: its CMake installation now includes `backend_network.py`.

`ROBOT_STATE_WS_URL`, `ROBOT_EXECUTION_WS_URL`, `ROBOT_SENSOR_WS_URL`, `ROBOT_APP_BACKEND_STATUS_URLS`, and platform `ros_backend.status_urls` are rejected when used as runtime overrides. Move those values into the shared file. Explicit constructor/CLI URLs remain available for isolated tests and tools; normal platform startup uses the file.

Loopback binding restricts network access to this host. It does not authenticate local processes. Remote deployment requires an intentional bind/client address choice and separate access controls.

## Verification

`tests.engine.robot.test_backend_network` checks custom nonconsecutive ports, platform/client agreement, launch-environment propagation, malformed configuration, legacy override rejection and backend loader parity. Packaging tests verify that target preparation includes the same file. No robot or network server is started by these tests.
