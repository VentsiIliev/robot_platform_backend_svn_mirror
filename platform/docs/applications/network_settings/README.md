# Network Settings

`NetworkSettings` is a shared application for host Wi-Fi, Ethernet, and IPv4
settings. Paint, Glue, Welding, and Twin systems register it in their Service
or Setup folder. The standalone `scripts/network_connect.py` launches the same
application; `src/applications/network_settings/example_usage.py` uses an
in-memory stub and does not change host networking.

The application follows the platform MVC flow: view signals → controller →
model → `INetworkSettingsService`. `NetworkSettingsService` selects the Linux
NetworkManager (`nmcli`) or Windows (`netsh`) backend extracted from the
original script. All scans and network changes run through `BackgroundWorker`
threads. The service validates IPv4 values before invoking OS commands.

The Wi-Fi page scans, connects, disconnects, forgets saved profiles, and edits
IPv4 settings for the active connection. The Wired page lists interfaces,
connects or disconnects them, and edits their IPv4 settings. Applying IPv4
settings can briefly interrupt connectivity because the OS backend reactivates
the connection.

Remote access is managed by the system installation rather than a platform
screen. Network Settings defaults to Wi-Fi and Wired tabs only. SSH and branded
RustDesk start at boot; see [installation](../../../packaging/remote_support/README.md).
The shell retains its active remote-session indicator. Passwords are managed
outside the platform.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `controller/` | [controller](controller/README.md) |
| `localization/` | [localization](localization/README.md) |
| `model/` | [model](model/README.md) |
| `service/` | [service](service/README.md) |
| `view/` | [view](view/README.md) |

[Complete source index](../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
