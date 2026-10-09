# Robot release and installer handoff

Recorded 2026-10-09. This is a session handoff, not a guarantee that local services
or VM state remain unchanged. Recheck current Git/config/VM state before acting.

## Objective and decisions

One complete robot release updates platform and backend together. Keep the update
service separate from the GUI/backend so activation can run after they stop.
Preserve live settings and machine-specific update-source configuration.

Remote support is an OS package, so compare its installed configured version with
the candidate release's expected version and reconcile it before activation.
Automatic kiosk upgrades are explicitly deferred by the user. Preserve kiosk
session/autologin settings during software updates. Do not reset the VM or create
new snapshots without a fresh instruction; the original clean snapshot matters.

## Repository and entry points

Combined checkout: `/home/ilv/Desktop/25488_ZeroErr_git`; platform is its subdirectory.
Current work branch at this handoff: `master`. `run_main.py` is a protected branch
name under the local agent instructions; do not commit/push from it.

From `platform/`:

```bash
source .venv/bin/activate
python3 -B packaging/robot/release_robot.py check paint_tray_dry
python3 -B packaging/robot/release_robot.py build paint_tray_dry
python3 -B packaging/robot/release_robot.py verify paint_tray_dry
```

Exact versions come from `config/platform.json`. Official builds require clean,
committed source; existing version archives are immutable. Increment robot/platform
versions for changed platform payloads and retain a validated backend version when
its code is unchanged. Reports: `dist/release-checks/`. Artifacts:
`../releases/paint_tray_dry/{platform,backend,robot}/VERSION/`.

Packaging ownership: `robot/` complete release orchestration and installer;
`platform/` PyInstaller/component-only tools; `runtime/` installed manage.py;
`shared/` archive/publication utilities; `kiosk/` machine desktop setup;
`remote_support/` package provisioning and configuration. Root/per-system wrapper
scripts were removed to avoid competing build paths. Guidance is consolidated in
`skills/`. Build/dist/htmlcov are generated output, not application source.

## Installed system

Root: `~/.local/share/robot-releases/paint_tray_dry` for desktop user `pl_user`.
`current` selects a release containing platform/backend/manifests; `launch.sh` and
versioned `tools` remain stable entry points. `data/` and `updates.json` are retained.

The user unit is `robot-update-paint_tray_dry.service`. GUI requests go through its
Unix socket. Offline locks prevent activation while the application is running.
The daemon stops the current bundled backend and activates both components.

```bash
systemctl --user status robot-update-paint_tray_dry.service
journalctl --user -u robot-update-paint_tray_dry.service -n 80 --no-pager
```

Native dependencies include zbar and Qt's XCB cursor library. Ubuntu Noble installs
`libzbar0t64` when requested through the compatible zbar package name. APT lock
waiting was added after unattended upgrades interrupted initial kiosk provisioning.
Do not interpret "platform installed" as proof that system setup completed; check
its marker, kiosk packages/session script and service state after a provisioning
failure. A normal software install preserves machine settings; explicit
`--setup-system` retries full provisioning.

## Remote-support change (committed, not rebuilt/VM-tested)

`packaging/remote_support/release.conf` pins download base, release tag, filename
and expected package version. At commit time: branded release
`v1.4.9-plproject.1`, `rustdesk-1.4.9.deb`, expected version `1.4.9`. Keep literal
assignments; the updater parses without executing Bash. New archives bundle the
configuration; editing source does not change existing archives.

`src/engine/updates/remote_support.py` checks `dpkg-query` status/version. An exact
configured match skips installation. A mismatch calls a scoped noninteractive sudo
helper; failure records a failed update and prevents candidate activation. Archives
without release.conf skip this check for compatibility.

Trusted initial/maintenance provisioning installs:

- `/usr/local/libexec/robot-remote-support-update` (root-owned Python helper).
- `/etc/robot-remote-support.json` (administrator-approved HTTPS download base).
- `/etc/sudoers.d/robot-remote-support-USER` (only helper `upgrade` authorization).

The helper validates identifiers and Debian metadata before APT installation.
Automatic updates do not execute release-owned installer shell scripts as root.
`NoNewPrivileges=true` was removed from the user service to permit scoped elevation.
Existing installations need one trusted maintenance install to bootstrap this
helper/service change. A changed trusted source requires administrator provisioning.

Support-package changes are outside application/data rollback. The dependency
upgrade itself has not been exercised on the VM yet; do not claim end-to-end
acceptance. Kiosk reconciliation is not implemented and was intentionally deferred.

## Verification and test limits

37 targeted tests passed for remote-support reconciliation, installer provisioning,
complete robot activation, updater IPC/service and packaging integration. Shell
syntax and `git diff --check` passed. The Unix-socket daemon test required execution
outside the sandbox; its initial sandbox failure was environmental.

The VM previously completed first installation with native dependencies and an
actual complete update from robot/platform 1.0.6 to 1.0.7, backend 1.0.1. That test
predates the new privileged remote-support helper. Frozen self-tests do not start
hardware/backend and do not replace real robot acceptance.

Last built artifacts reported in the session: robot/platform 1.0.7, backend 1.0.1.
Build a fresh version to test the newly committed support payload. Do not overwrite
1.0.7 or assume its archive contains later source changes.

## VM and local feed (last known)

VM: `robot-install-test`, libvirt `qemu:///session`, Ubuntu 24.04, user `pl_user`.
Disks/backing chain were moved to internal storage under
`/home/ilv/VirtualMachines/robot-install-test/`; external SSD sharing was detached.
The original clean baseline was retained. The SSD is no longer required for that
saved VM setup, provided its internal backing files remain intact.

Host test feed: `platform/dist/install-tests/complete-updates/`, HTTP port 8768.
VM reaches it as `http://10.0.2.2:8768/`. The temporary HTTP server may have exited;
check it before guest downloads. This local feed is independent of Gitea and does
not publish official artifacts. The configure-test-feed helper backs up updates.json
and explicitly enables insecure HTTP for this local test.

Stopping `gdm3` caused a black display. A later logout black-screen incident was
resolved by switching back to the greeter's VT1; the underlying cause was not
proven fixed. Do not stop GDM to transfer archives or install software. Use console
VT switching or authenticated SSH when available. Guest agent/SSH connectivity was
not reliably available for the NAT VM; do not confuse it with the physical machine
at 192.168.222.112. That physical machine's old 1.0.1 install root was removed by
the user during the session.

## Source publication status

Remote-support implementation commit: `3c6afff`.
SVN publication succeeded as revision 49; SVN-generated commit `ee80d44`.
Master synchronization merge: `06069c6`. Working tree was clean after publication,
before this documentation task.

SVN: `https://192.168.2.101:8443/svn/25488_ZeroErr/trunk`.
Gitea remote `gitea-test`:
`http://192.168.222.112:3000/plproject/25488_ZeroErr_test.git`.
Gitea push from the agent failed because no interactive credentials were available.
The user was told to run `git push gitea-test master`; completion is unconfirmed.
Never record passwords/tokens in this document, artifacts or command output.

Master contains merged SVN-generated history. In this session, safe SVN publication
used an isolated checkout based on `refs/remotes/git-svn`, applied the final tree
delta, committed/dcommitted it, verified tree equality, then merged the SVN-generated
commit back to master. Blind dcommit from the merged work history had risked replaying
already published changes. Inspect history before choosing the next publication path.

## Next useful work

Build a fresh release and run one trusted maintenance install on the test VM to
bootstrap the helper. Test equal-version skip, changed-version upgrade, and a
failed required upgrade retaining the old robot release. Check that kiosk settings
are preserved. Confirm Gitea source push separately from artifact publication.
Keep hardware acceptance and deferred kiosk update design separate.

Documentation edited in this follow-up is not automatically committed or published.
