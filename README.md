# 25488 ZeroErr — Robot Application Platform

Robot control and operator applications for the ZeroErr edge-painting cell. This repository contains the Qt platform, ROS 2 backend, deployment tooling, and earlier application sources.

**SVN is the authoritative source; GitHub (`VentsiIliev/robot_platform_backend_svn_mirror`) mirrors its published history.** Platform, backend and PL PROJECT remote control are maintained together here. The former standalone remote-support repository is historical only. A future move to separate GitLab projects is not configured.

## Repository layout

| Directory | Purpose |
|---|---|
| `platform/` | Python/PyQt6 operator application, robot-system definitions, services, tests, and documentation |
| `backend/ros2_ws/` | ROS 2 workspace and ZeroErr backend launch scripts |
| `plproject_remote_control/` | PL PROJECT branded RustDesk source, vendored shared dependency and build documentation |
| `platform/packaging/` | Platform and complete robot builds, installers and publication |
| `deployment/` | Deployment reference documentation |
| `25488_CobotEdgePaintingZeroErr/` | Earlier application sources and supporting project material |
| `releases/` | Locally generated release artifacts; excluded from version control |

The platform separates shared infrastructure, robot-system composition, and MVC applications. See the [robot-system overview](platform/docs/robot_systems/README.md) and [coding guidance](platform/AGENTS.md).

## Clone and prepare a test checkout

```bash
git clone https://github.com/VentsiIliev/robot_platform_backend_svn_mirror.git
cd robot_platform_backend_svn_mirror/platform
./launch_robot_app.sh --setup-only
```

This GitHub clone is for browsing and development. SVN publication uses the existing git-svn checkout.

The current deployment target is Ubuntu 24.04 with Python 3.12 and ROS 2 Jazzy. The source launcher creates `platform/.venv`, installs `requirements.txt`, and verifies Python/native imports. On Ubuntu/Debian it installs missing `libzbar0` and `libxcb-cursor0` system libraries using `sudo` when required. If Python environment creation fails, install `python3-venv` and retry.

`--setup-only` prepares the platform environment without starting the application or robot services. It does not install ROS, MoveIt, EtherCAT drivers, or build the backend workspace.

## Run the platform

From `platform/`:

```bash
./launch_robot_app.sh
```

The launcher isolates PyQt6 from OpenCV's bundled Qt plugin paths. In an interactive terminal, press **Ctrl+X** to stop the application.

Runtime selection lives in [platform/config/platform.json](platform/config/platform.json). The checked-in configuration selects `paint_tray_dry`, the ZeroErr driver, and backend profile `paint_short_links`; it enables backend auto-start/stop and development login bypass. Inspect this configuration before launching on a machine connected to hardware.

The configured backend entry point is `backend/ros2_ws/launch_zeroerr.sh`. ROS/MoveIt, backend Python requirements, and EtherCAT support must be provisioned separately. The current verified combined release target is `paint_tray_dry`; entries for other targets must be explicitly configured and validated. See [deployment prerequisites and release commands](deployment/README.md).

## Machine configuration and storage

A clone provides source and translation catalogs, not an existing cell's configuration. Machine settings, accounts, workpieces, calibration matrices, and generated ROS build outputs are excluded from version control. Missing settings may be created from serializer defaults; these do not reproduce a commissioned machine.

Each paint system owns its source storage:

| System | Source storage |
|---|---|
| `paint` | `platform/src/robot_systems/paint/storage/` |
| `paint_auto_dry` | `platform/src/robot_systems/paint_auto_dry/storage/` |
| `paint_tray_dry` | `platform/src/robot_systems/paint_tray_dry/storage/` |

Shared painting implementation remains under `paint/`. Each dryer package owns its system class and `paint_system_config.py` overrides.

With `ROBOT_PLATFORM_DATA_ROOT` set, writable paths resolve beneath `<data_root>/<system>/storage/`. Translation catalogs remain application resources. The platform-only updater migrates legacy `paint/profiles/<profile>/storage/` in its staged data copy and preserves rollback data. This behavior is separate from the combined robot installer, whose rollback switches code without reversing machine settings/schema changes.

See [paint storage ownership](platform/docs/robot_systems/paint/README.md), [platform installer and updates](platform/packaging/platform/README.md), and [combined deployment](deployment/README.md). Back up and transfer machine data separately when reproducing an existing cell.

## Publish changes to SVN and GitHub

SVN trunk: `https://192.168.2.101:8443/svn/25488_ZeroErr/trunk`.
GitHub mirror: `https://github.com/VentsiIliev/robot_platform_backend_svn_mirror`.

From the main git-svn checkout on the `master` work branch:

```bash
python3 platform/scripts/publish_changes.py -m "Describe the completed change" paths/to/changes
# For already committed changes or publication retries:
python3 platform/scripts/publish_changes.py --resume
```

The script commits, runs `git svn dcommit`, and pushes the SVN-generated history
to `github-svn-mirror`. Do not push pre-dcommit history or merge duplicated SVN
history into the publication branch. The `run_main.py` branch is protected.
A rejected push requires inspecting the histories; do not blindly force-push.

Git release tags are separate from SVN tags. Publish intended release tags to
GitHub explicitly after source publication. Remote-control build instructions
and release requirements are in [plproject_remote_control](plproject_remote_control/SVN_IMPORT.md).

To refresh a GitHub test clone with no conflicting local changes:

```bash
git pull --ff-only origin master
```

Keep experiments on separate branches. Gitea and GitLab are not current
publication destinations.

## Tests and documentation

Prepare the platform environment first, then run from `platform/`:

```bash
.venv/bin/python tests/run_tests.py
.venv/bin/python -m unittest tests.robot_systems.paint.test_paint_profiles -v
python3 serve_docs.py --no-open
```

The documentation server defaults to port 7000. The test runner uses Qt's offscreen platform; hardware commissioning remains a separate verification step.

Useful entry points:

- [Engine services](platform/docs/engine/README.md)
- [Applications](platform/docs/applications/README.md)
- [Robot systems](platform/docs/robot_systems/README.md)
- [Paint system and storage](platform/docs/robot_systems/paint/README.md)
- [Platform setup, packaging, and updates](platform/packaging/platform/README.md)
- [Combined robot release workflow](deployment/README.md)

## Startup troubleshooting

| Symptom | Next check |
|---|---|
| Python environment creation fails | Install `python3-venv`; verify the Python version |
| Missing ZBar or XCB cursor library | Rerun the updated launcher and complete its sudo installation |
| Qt plugin initialization fails | Check the reported shared-library/display error; use the launcher to isolate OpenCV's Qt environment |
| Backend connection refused on ports 5000–5003 | Inspect `/tmp/robot_app_zeroerr_backend.log` and verify ROS/backend prerequisites |
| Missing calibration or unknown hardware mapping | Restore or commission the selected system's machine configuration |
| Gitea reports “Push to create is not enabled” | Verify the repository exists and that the remote URL names its owner, not the collaborator's login |
| Non-fast-forward after SVN publication | Check whether commits were pushed before `git svn dcommit` rewrote their IDs |
