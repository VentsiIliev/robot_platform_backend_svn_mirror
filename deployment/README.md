# Robot-system releases

Edit `platform/config/platform.json` only. The selected entry under `robot_systems`
contains `robot_driver`, `backend`, `backend_profile`, `release_version`,
`platform_version`, and `backend_version`. Missing/incomplete entries fail.
Only `paint_tray_dry` / ZeroErr / `paint_short_links` is configured and verified today.
Other targets require explicit entries; Fairino backend packaging is not implemented.
The existing release-target catalog is internal build metadata (product names,
package inclusion, storage profile), not another runtime configuration to maintain.

## Verify current source

From `~/Desktop/25488_ZeroErr_git`, on Ubuntu 24.04 / ROS Jazzy:

```bash
python3 deployment/scripts/package_backend.py paint_tray_dry --verify-only
python3 deployment/scripts/package_platform.py paint_tray_dry --verify-only
python3 -B deployment/scripts/test_packaging.py
```

Platform builds use `platform/.venv`; install `platform/packaging/requirements-build.txt`
there first. Verification builds run self-tests without starting backend nodes or hardware.
ROS/MoveIt, Python backend requirements, and the EtherLab master/kernel driver are
machine prerequisites. Backend archives include requirement lists; the apt list also
contains build tooling. Hardware deployment still needs validation on the target machine.

## Publish component archives and assemble a robot release

Commit source changes first. Component packagers reject dirty source and refuse to
replace an existing version. Upload the source to SVN before an official build so
its manifest contains the SVN revision. These commands do not commit or upload source.

```bash
python3 deployment/scripts/package_backend.py paint_tray_dry
python3 deployment/scripts/package_platform.py paint_tray_dry
python3 deployment/scripts/package_robot.py paint_tray_dry
python3 deployment/scripts/tag_robot.py paint_tray_dry
```

Build a component only when its selected version does not already exist. For a
platform-only change, increase `platform_version` and `release_version`, build the
platform, then assemble using the existing `backend_version`. Backend profile/driver
changes require matching component archives. Robot assembly checks exact versions,
checksums, OS/architecture and target/profile identity. It never substitutes the
current development backend for a missing published version.

Outputs: `releases/<target>/<platform|backend|robot>/<version>/`, each containing an
archive, SHA256 file and manifest. Robot manifest pins both component manifests.
The generated runtime `platform.json` selects exactly that target and launches the
backend bundled beside the platform. Live machine settings are not packaged.

`tag_robot.py` creates immutable local annotated Git tags such as
`paint_tray_dry/backend/v1.0.0`, `paint_tray_dry/platform/v1.0.0`, and
`paint_tray_dry/robot/v1.0.0`, pointing to the recorded source commits. Repeated tags
must point to the same commit. Git tags do not become SVN tags through `git svn dcommit`.
SVN tag publication and remote artifact hosting remain separate, unimplemented steps.

## Install and roll back

Verify the robot archive SHA256 against its accompanying checksum, extract it,
and run its installer (does not start hardware):

```bash
python3 robot/install.py
```

Default installation: `~/.local/share/robot-releases/<target>/`. The installer stores
versioned releases, preserves `data/`, and atomically switches `current` for both
components. Start using the installed `launch.sh`; this holds a lock preventing
installation/activation while the app is running. Backend auto-start/stop is enabled
in the generated package configuration. Close the app and independently stop any
manually launched backend before switching versions.

```bash
python3 robot/install.py --activate 1.0.0
```

`--root` optionally selects a different installation directory. Rollback switches
code only; it does not reverse machine settings/schema changes. The existing
platform-only updater is disabled for combined installations; use the combined
installer to keep platform/backend versions together. No automatic schema migration
or combined remote-update service is implemented yet.
