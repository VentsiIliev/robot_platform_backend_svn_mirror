# Remote support packaging

The [operational guide](../../../packaging/remote_support/README.md) describes
initial provisioning, version configuration and automatic upgrades.

`build_payload.py` bundles the installer, literal `release.conf`, privileged
package helper and helper provisioning script. First installation provisions
SSH/native libraries, installs branded RustDesk and enables boot services.
A trusted maintenance installation refreshes helper policy and reconciles the
support version without rerunning kiosk setup.

The automatic updater compares the candidate's expected version to the installed
configured package, then uses the root-owned helper only if they differ.
The helper permits packages from the administrator-configured HTTPS source and
verifies Debian metadata before installation. Legacy timed-access services are
retired by provisioning; they are not the current update-service architecture.

[Engine updater](../../engine/updates/README.md) documents activation behavior.
