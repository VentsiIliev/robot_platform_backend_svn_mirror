# Remote support packaging

The [operational guide](../../../packaging/remote_support/README.md) describes
initial provisioning, version configuration and automatic upgrades.

`build_payload.py` bundles the installer, literal `release.conf`, privileged
package helper and helper provisioning script. `install.sh` orchestrates
standalone component installers for OpenSSH, branded RustDesk, the auto-login
helper and update-helper provisioning. Each component can be rerun independently
for replacement or diagnostics without repeating successful components.

First installation provisions SSH/native libraries, installs branded RustDesk
and enables boot services. The RustDesk component also owns retirement of the
legacy timed-access units, ensuring that migration precedes permanent service
activation.
A trusted maintenance installation refreshes helper policy and reconciles the
support version without rerunning kiosk setup.

The automatic updater compares the candidate's expected version to the installed
configured package, then uses the root-owned helper only if they differ.
The helper permits packages from the administrator-configured HTTPS source and
verifies Debian metadata before installation. Legacy timed-access services are
retired by provisioning; they are not the current update-service architecture.

[Engine updater](../../engine/updates/README.md) documents activation behavior.
