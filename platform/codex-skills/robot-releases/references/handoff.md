# Handoff: combined robot releases and paint overrides

Snapshot: 2026-10-06. Verify current state before acting.

## Locate the correct checkout

- Active combined Git/SVN checkout: `/home/ilv/Desktop/25488_ZeroErr_git`.
  Contains `platform/`, `backend/ros2_ws/`, `deployment/`, ignored `releases/`.
- `/home/ilv/Desktop/robot_app_platform` is the older standalone platform checkout.
  A session may start there even though this work belongs in the combined checkout.
- `/home/ilv/ros2_ws` is the older standalone backend workspace.
- Do not silently edit all three copies. Read-only inspection may help diagnose an
  old installation, but deployment implementation lives in the combined checkout.
- A clean temporary worktree used for builds was
  `/tmp/paint-tray-dry-release-d0ecf21`; it is disposable and must not become a dependency.
- Session write permissions historically covered the old platform checkout and
  `/tmp`; writing the combined checkout required tool escalation. Check current permissions.

## Source and publication state

SVN trunk: `https://192.168.2.101:8443/svn/25488_ZeroErr/trunk`.
Current work branch at handoff: `master` (the protected branch named `run_main.py`
was not used). Uploaded changes:

- r13: initial combined import, Git `8e16c65329a76e6ecf4100e3f909d7ec4a59910e`.
- r14: packaging/configuration, Git `02a6bd566b59c0325927be463353a6073531d7e1`.
- r15: isolated paint overrides and combined install/run scripts,
  Git `68d7d4296f33d0b3eeb6102f37e2cce7033d2cd2`.

Two user-owned staged deletions were deliberately preserved and excluded from
those uploads: `platform/compute_offsets.py` and `platform/src/bootstrap/preview.txt`.
Inspect status; do not include or restore these without task authorization.
To publish without disturbing them, prior work committed only task paths, used a
clean worktree for `git svn dcommit`, then aligned master only after confirming
its tree exactly matched the rewritten SVN tree. Git-SVN rewrites commit IDs;
existing annotated tags/artifact source hashes still identify the original builds.

## User's chosen configuration contract

The user wants minimal terminal parameters and one maintained selection file:
`platform/config/platform.json`. `robot_system` selects an explicit entry under
`robot_systems`. A supported-system list does not constitute a configuration.
A missing selected entry must fail even if backend auto-launch is disabled.

Currently only this entry is configured:

```json
"paint_tray_dry": {
  "robot_driver": "zeroerr",
  "backend": "zeroerr",
  "backend_profile": "paint_short_links",
  "release_version": "1.0.0",
  "platform_version": "1.0.0",
  "backend_version": "1.0.0"
}
```

All required fields are validated; versions use major.minor.patch. Driver/backend
must match. `zeroerr` and `fairino` are recognized identifiers, but backend launch
and packaging currently implement only ZeroErr. Do not invent the remaining
systems' mappings. Both supported ROS robot types use the platform's existing
`Ros2Robot` bridge contract at localhost:5000; `zeroerr_robot.py` is not a usable
separate implementation. `build_configured_robot()` validates this selection and
replaces provider hard-coded driver selection in normal bootstrap.

`platform/config/release_targets.json` remains internal build metadata: product
names, included Python packages, storage/profile identity. It is not another user
release-selection file. `backend_targets.json` and deployment `backend.VERSION`
were removed. Older robot-system `VERSION` files/wrappers still exist for the
legacy platform-only workflow; new deployment scripts use platform.json versions.

## Implementation map

- `platform/src/bootstrap/startup_config.py`: selection validation and configured
  bridge construction. `run_main.py` loads it before system composition.
- `platform/src/bootstrap/ros_backend_launcher.py`: same selected target/profile;
  source launch resolves sibling `backend/ros2_ws`, frozen launch resolves
  `../backend` relative to the platform executable. Rejects conflicting script paths.
  Existing-backend reuse validates `robot_release.target/profile` in health JSON.
- Backend `zeroerr/launch/zeroerr_launch/runtime_config.py`: validates and applies
  `ZEROERR_ACTIVE_PROFILE` before loading profile runtime configuration.
- Backend shared `erob_moveit_runtime/scripts/rest/server.py`: health/startup JSON
  reports target/profile from environment. Cold-start readiness/actual runtime
  identity are not exhaustively tested; this metadata reflects requested env values.
- `platform/packaging/platform/targets.py`: generates packaged platform.json with
  one selected system, backend auto-launch/stop enabled, no developer script paths.
- `deployment/scripts/package_backend.py TARGET`: isolated ROS Jazzy merged install,
  no source symlink install, relocation/package-discovery checks, archive/checksum/manifest.
  Dependencies: Ubuntu 24.04, ROS/MoveIt, EtherLab master/kernel driver, backend Python deps.
- `package_platform.py TARGET`: existing PyInstaller build + frozen `--self-test`,
  immutable platform component archive. Uses `platform/.venv` and declared build requirements.
- `package_robot.py TARGET`: loads exact published component versions, validates
  checksums/target/profile/OS/architecture, creates combined archive/installer/manifest.
  Does not rebuild or substitute current source when a component version is missing.
- `release_common.py`: shared component selection, digest, extraction and source identity.
- `install_robot.py` (copied as `robot/install.py`): versioned installation, persistent
  data outside releases, atomic `current`, shared runtime lock/exclusive activation,
  rollback by `--activate VERSION`. Does not migrate/revert persisted data schemas.
  Disables the existing platform-only updater for combined installs.
- `manage_robot.py install|run TARGET`: checksum-verifies and installs the configured
  combined archive, or runs the activated combined installation.
- `tag_robot.py TARGET`: local annotated tags for exact component/robot source commits.
  Git tags are not published as SVN tags by dcommit. SVN tagging/remote hosting not implemented.

Most scripts accept TARGET only; verify builds also accept `--verify-only`.
Official builds reject dirty source and existing version output directories.
For a platform-only update, increment platform_version and release_version,
retain the tested backend_version, build platform and assemble that exact pair.

## Artifacts already produced

Combined checkout contains ignored `releases/paint_tray_dry/{backend,platform,robot}/1.0.0/`.
Robot archive: `paint_tray_dry-robot-1.0.0-x86_64.tar.gz` (about 297 MiB), with
SHA256 file and manifest. Local annotated tags:

- `paint_tray_dry/backend/v1.0.0`
- `paint_tray_dry/platform/v1.0.0`
- `paint_tray_dry/robot/v1.0.0`

These artifacts were built from pre-dcommit Git `d0ecf21` before the overrides.
Their SVN revision fields are null because the build preceded SVN upload.
Do not overwrite them or retarget their tags. A next platform release is needed
for the per-system override source now in r15; backend 1.0.0 can be reused.

## Installation confusion already encountered

Combined installation root: `~/.local/share/robot-releases/paint_tray_dry`.
Older platform-only root: `~/.local/share/robot-platform/products/paint-tray-dry-robot`.

The user ran old `run_latest.sh` from `robot_app_platform`; it started the older
platform installation and attempted `/home/ilv/ros2_ws/launch_zeroerr.sh`.
Connection-refused logs alone did not prove failure of the new combined archive.
Then combined-checkout `install_latest.sh` initially still sought an old platform
installer under `platform/dist/platform-releases`; this wrapper mismatch was fixed
in r15. Combined-checkout install/run wrappers now route to manage_robot.py when
that deployment script is present; standalone checkouts retain legacy fallback.
The older checkout's wrappers were not changed.

From combined `platform/src/robot_systems/paint_tray_dry`, use `./install_latest.sh`,
then `./run_latest.sh`. Close the old GUI and stop separately launched backend
processes first. No real machine installation or hardware startup was performed
by the agent; installation was verified only in temporary directories. The user
still needs to verify startup with the correct combined installation.

## Per-system paint overrides

Shared defaults: `platform/src/robot_systems/paint/paint_system_config.py`.
Empty, documented override files now exist at:

- `platform/src/robot_systems/paint_auto_dry/paint_system_config.py`
- `platform/src/robot_systems/paint_tray_dry/paint_system_config.py`

Declare only constants that differ, with the same names as the shared defaults.
Their bootstrap providers call `with_paint_system_overrides()` in the shared
paint_robot_system module. It creates an isolated subclass/configuration, rebuilding
application specs and dashboard UI settings without mutating shared classes/modules.
Preserves tray-specific controls, allowed strategies, settings and metadata.
Unknown uppercase override names fail. Contour diagnostic bypass now reads the
selected robot system's config in application_wiring. These switches are compiled
source configuration, not editable runtime machine JSON settings.

The shared paint module must not eagerly import both sibling override modules:
PyInstaller deliberately excludes the non-selected system. Profile providers own
those imports. Normal paint uses shared defaults.

## Verification and outstanding work

Passed: backend build of 10 ROS packages and relocation/discovery checks; frozen
platform self-test before and after overrides; exact-pair assembly/checksums;
real archive extraction, temporary installation and installed frozen self-test;
rollback/data preservation/runtime lock/traversal/mismatch integration checks.
No nodes, drive enable, GUI main loop, or hardware were invoked in these checks.

Useful commands from combined root:

```bash
python3 -B deployment/scripts/test_packaging.py
cd platform
PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=/tmp/robot-release-mpl .venv/bin/python -m unittest tests.robot_systems.paint.test_paint_system_overrides tests.bootstrap.test_startup_config -q
```

20 targeted override/startup tests passed; 44 startup/release tests and 4 packaging
integration tests passed earlier. Broader `test_paint_system_integration` has 4
failures + 3 errors, reproduced on the pre-override checkout: stale service fixtures,
contour-editor dependency API mismatch (`ContourEditorUiConfig` missing), etc.
Do not claim a clean full suite. Frozen self-test is limited and does not exercise
all lazy production applications or real hardware startup.

Next likely work: verify actual combined runtime startup; publish a new platform/
robot version containing overrides; map other systems explicitly; add Fairino
packaging only when needed; implement SVN tag publication, remote artifact hosting,
combined remote updates and data/schema migration if requested. None of these is
implicitly authorized by reading this handoff.
