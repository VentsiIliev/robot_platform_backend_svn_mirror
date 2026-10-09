# Boot-managed remote support

`RustDeskServiceStatusClient` reads `LoadState`, `ActiveState` and `UnitFileState`
from systemd with a bounded timeout. The shell monitor uses this
read-only status client; they do not control service startup. RustDesk session monitoring continues using its existing IPC protocol.
The Remote Support application and its password controls have been removed.

The platform installation step installs OpenSSH server and the branded RustDesk
package, validates SSH configuration and enables both services at boot. It also
retires the former timed-access controller socket, expiry service/timer and
RustDesk startup gate. The legacy controller implementation remains for older
clients/tests but is not installed or enabled by new release payloads.

See [installation and migration](../../../packaging/remote_support/README.md)
for commands and target-machine verification.
