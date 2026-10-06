# Remote Support

Paint registers `RemoteSupport` in Administration, with Admin access by default.
Its Network Settings screen contains only Wi-Fi and Wired tabs. The header
shows an icon only while an authenticated incoming desktop session is active.

The Access tab offers 15 minutes, 2 hours, and 5 hours. Choose the duration,
then enable support. The window starts immediately and displays remaining time.
It expires even if the GUI closes, and reboot ends access. Changing the selected
duration or a remote password does not extend a running window.

The Unattended Access tab supports setting/changing a password, resetting a
forgotten remote password, and removing unattended access. All mutations require
an existing platform Admin user ID and password, verified through the same
user repository as login. Reset does not require the old remote password.
New remote passwords must match their confirmation and contain 8–64 characters.
Secret fields clear when submitted or the screen is closed. Password state is
shown without displaying the saved password.

Password changes affect future connections; existing sessions continue until
support is disabled or expires. Removal restores local approval and disables
permanent-password login, including branded preset credentials. RustDesk's
user daemon must be available for password management. Enable a timed access
window first; the password tab shows this prerequisite while support is OFF.
The app does not start support to change a password. If platform Admin credentials are also forgotten,
use the separate local administrator recovery procedure.

The application follows MVC and uses BackgroundWorker for all socket and
authentication operations. Its service depends on IAuthenticationService;
Paint supplies AuthenticationService with its CSV user-repository adapter.
English and Bulgarian catalogs support initial render and language switching.

Install the upgraded local controller and systemd watchdog before using timed
access; see [controller deployment](../../engine/remote_support/README.md).
The application refuses unbounded enable operations through older controllers.

Standalone, hardware-free preview:

```bash
python src/applications/remote_support/example_usage.py
```

The development stub accepts the test Admin ID/password `admin`/`admin` only.
Production uses existing platform users and introduces no default credentials.

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
