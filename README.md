# 25488 ZeroErr — Robot Application Platform

Robot control and operator applications for the ZeroErr edge-painting cell. This repository contains the Qt platform, ROS 2 backend, deployment tooling, and earlier application sources.

Source is maintained in both SVN and Gitea. **SVN is the authoritative publication path; Gitea hosts the Git copy for browsing, collaboration, and testing.** Publish through SVN before pushing shared changes to Gitea.

## Repository layout

| Directory | Purpose |
|---|---|
| `platform/` | Python/PyQt6 operator application, robot-system definitions, services, tests, and documentation |
| `backend/ros2_ws/` | ROS 2 workspace and ZeroErr backend launch scripts |
| `deployment/` | Component packaging, combined robot releases, installation, and release tags |
| `25488_CobotEdgePaintingZeroErr/` | Earlier application sources and supporting project material |
| `releases/` | Locally generated release artifacts; excluded from version control |

The platform separates shared infrastructure, robot-system composition, and MVC applications. See the [robot-system overview](platform/docs/robot_systems/README.md) and [coding guidance](platform/AGENTS.md).

## Clone and prepare a test checkout

```bash
git clone http://192.168.222.112:3000/admin/25488_ZeroErr_test.git
cd 25488_ZeroErr_test/platform
./launch_robot_app.sh --setup-only
```

The repository owner is `admin`; authenticate with your own Gitea account if it has access. Access to this private-network host is required. Use the clone URL displayed by Gitea if the repository is renamed or transferred.

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

## Publish changes to SVN and Gitea

SVN trunk:

```text
https://192.168.2.101:8443/svn/25488_ZeroErr/trunk
```

Gitea test repository:

```text
http://192.168.222.112:3000/admin/25488_ZeroErr_test
```

The main development checkout is a `git svn` checkout. A normal Gitea clone does not include its SVN connection metadata. Keep the main checkout for SVN publication and use separate Gitea clones/branches for experiments.

For the current shared `master` workflow, review and stage your intended files, commit locally, publish all pending local commits to SVN, then push the resulting Git history:

```bash
git status
git diff --cached
# Stage the specific files you intend to publish before committing.
git commit -m "Describe the completed change"
git svn dcommit
git push gitea-test master
```

Run these steps individually and stop if any step fails. `git svn dcommit` publishes all pending commits since the SVN tracking revision, not only the most recent one, and may rewrite their Git IDs to add SVN metadata. **Do not push those commits to Gitea first.** Once both repositories share the SVN-generated history, subsequent SVN-first pushes normally fast-forward.

If `gitea-test` is not configured, add it once:

```bash
git remote add gitea-test http://192.168.222.112:3000/admin/25488_ZeroErr_test.git
```

If it already exists, update it with `git remote set-url` instead. A rejected push requires inspecting the histories. Do not merge the pre-SVN history back into the SVN publication branch or blindly force-push over collaborators' work. A deliberate history correction requires a guarded push and coordination with existing clones.

Git release tags are separate from SVN tags. Publish intended Git tags to Gitea explicitly; `git svn dcommit` does not publish them as SVN tags. See [release tagging](deployment/README.md).

### Refresh a Gitea test clone

From the repository root, with no conflicting local changes:

```bash
git pull --ff-only origin master
cd platform
./launch_robot_app.sh
```

Keep experiments on separate branches. If a deliberate history correction prevents a fast-forward, preserve local work and coordinate recovery rather than merging duplicate SVN/Git histories.

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
