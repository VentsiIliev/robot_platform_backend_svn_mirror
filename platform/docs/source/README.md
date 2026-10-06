# Files directly under `src/`

`__init__.py` establishes the source namespace. `cam_server.py` is a standalone Flask MJPEG camera server, separate from the main application bootstrap. It opens camera 0 (1280×720/30 fps), configures auto-exposure and starts a capture thread at module import; importing it is therefore not a hardware-free operation. Its explicit main entry binds port 5005 on all interfaces, exposes a video stream and auto-exposure control, and registers camera cleanup.

Production GUI startup is [src/bootstrap](../bootstrap/README.md), not this camera server. Use the module/source reference to inspect its endpoints and thread ownership before running it.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `applications/` | [applications](../applications/README.md) |
| `bootstrap/` | [bootstrap](../bootstrap/README.md) |
| `engine/` | [engine](../engine/README.md) |
| `robot_systems/` | [robot_systems](../robot_systems/README.md) |
| `shared_contracts/` | [shared_contracts](../shared_contracts/README.md) |

[Complete source index](../SOURCE_INDEX.md).
<!-- source-navigation:end -->
