---
name: robot-releases
description: Build and verify this repository's robot releases, prepare LAN update feeds, diagnose machine update connectivity, or prepare SVN/GitHub release publication. Includes release-scope questions, component compatibility, kiosk credential confirmation, and installation verification. Use for deployment and update delivery, not general robot motion or calibration changes.
---

# Robot releases

Produce a verified artifact for the requested machine and delivery method. A built
bundle, a verified installer, a LAN feed, and a published GitHub release are
different outcomes: report exactly which ones were completed.

## 1. Establish the checkout and current rules

Locate the combined Git root and its `platform/` directory. Run the commands below
from `platform/` unless stated otherwise. Read its `AGENTS.md`,
`packaging/robot/README.md`, and `config/platform.json`. Read
`packaging/platform/README.md` when a platform-only installer is relevant.

Treat `config/platform.json` as the release selection authority. The product map
and package selection are in `config/release_targets.json`. Do not recreate a
second selection registry. Discover the existing packagers before writing helpers.

Check Git status across the **combined repository**, the current branch, installed
dependency locations, existing release artifacts, build prerequisites, and disk
space. Root `scripts/` remains excluded except for an explicitly required helper
such as the source publication command named in `AGENTS.md`.

## 2. Resolve only the unanswered release questions

First use the conversation, installed manifests, configuration and existing
artifacts. Ask early about material unknowns, preferably as one short group, and
continue independent inspection while waiting. Do not ask again when the user
already supplied the answer or authorized the action.

| Missing decision | Question or evidence to obtain |
| --- | --- |
| Target machine | Which robot system/product, installed release, OS and CPU architecture? |
| Artifact format | Combined robot update or standalone platform installer? An existing combined robot updater needs a combined archive even for a UI-only change. |
| Delivery | Build files only, make them available on the existing LAN feed, or publish to SVN/GitHub? A request to build alone does not authorize remote publication. |
| Change scope | Which changes belong in this release? Resolve unrelated or mixed edits before staging them. |
| Backend reuse | Reuse the installed backend version/profile, or intentionally release a changed backend? Compare manifests before asking. |
| Kiosk credential | May this build reuse the existing kiosk exit-password credential, or is another credential required? Explain that `packaging/platform/build.py` explicitly requires this choice. |
| Update trust | For remote delivery, which source/channel and existing signature/key configuration does the station use? Read the station configuration when accessible. |

Infer settled choices. For example, a machine running a combined release and
using its Software Update screen establishes the required archive format.
Likewise, a user already requesting delivery through its configured LAN feed need
not approve that same delivery again. Confirm a missing credential decision once;
an unrelated reply such as “the update check works” is not credential approval.

State the resulting plan: target, change scope, new platform/robot versions,
backend version/profile, artifact format, delivery destination and credential
choice. Keep application/build work progressing until an actual prerequisite
requires an answer. Do not end with a generic request to continue.

## 3. Reconcile versions and backend compatibility

Inspect the station's installed `manifest.json`, its `selection` and component
manifests, and `releases/TARGET/{platform,backend,robot}/` under the combined root.
Check the current feed and existing tags where relevant. Choose an unused version;
do not rely only on `src/robot_systems/TARGET/VERSION`, which can lag behind the
combined release pins.

- For a UI/platform-only change delivered as a combined update, increment
  `platform_version` and `release_version`; retain the validated backend version.
- Preserve the backend's exact `backend_profile` when reusing it. A changed profile
  name can make an otherwise unchanged archive incompatible. Ask when the intended
  machine configuration and source configuration disagree; do not silently select
  whichever makes packaging succeed.
- An intended backend change needs its own new backend version and verified
  build. Never relabel an old backend archive to satisfy a new profile.
- Update the selected `config/platform.json` entry and, when relevant, the target's
  `VERSION` file. Leave other targets unchanged.
- Existing release files, versions, and tags are immutable. A retry may verify an
  existing artifact; a different payload needs a new version.

## 4. Prepare clean, scoped source and dependencies

Combined builds call `source_identity()` and require a clean, committed **whole
repository**. `check` accepts uncommitted source. Never bypass this gate, hide
changed source in ignore rules, or commit unrelated user work.

Use the current work branch for requested source commits/publication, respecting
the protected branch rules in `AGENTS.md`. If unrelated edits prevent a local test
build, an isolated clone/worktree with a scoped local commit can preserve the
user's working copy. Read [source-snapshots.md](references/source-snapshots.md) for
that case or when a locally modified dependency is involved. Clearly distinguish
that local snapshot from source published to SVN/GitHub.

If required tests fail, diagnose the cause and fix only an authorized, understood
problem. Explain configuration/behavior tradeoffs before changing them. Do not
disable backend identity guards, skip failed stages, or bundle unrelated fixes to
force a release through.

## 5. Run the release gate and relevant change checks

Set `TARGET` to the confirmed target; `paint_tray_dry` is only an example:

```bash
TARGET=paint_tray_dry
QT_QPA_PLATFORM=offscreen .venv/bin/python -B packaging/robot/release_robot.py check "$TARGET"
```

Run the smallest meaningful tests for the changed behavior as well. UI changes
need an offscreen construction/render or interaction check when practical.
Do not launch the normal robot application as a packaging smoke test: it may
start backend processes and access hardware.

The updater tests use temporary local sockets. An `Operation not permitted` error
from a restricted sandbox needs the appropriate execution permission, not weakened
tests or production code. Distinguish real failures from intentionally failing
fixture commands printed by orchestration tests. Check the final exit status and
the correct JSON report in `dist/release-checks/`.

## 6. Confirm and validate the kiosk credential

The default file is `~/.config/pl-project/kiosk-password.json`;
`PL_KIOSK_PASSWORD_FILE` selects another file. Validate it through
`src.bootstrap.kiosk_password.KioskPassword` without printing its contents.
Do not ask for a plaintext password in chat or expose the hash in logs.

After explicit confirmation already obtained in step 2, set
`PL_KIOSK_PASSWORD_CONFIRMED=1` for the noninteractive build. Do not set it in
advance as a way to bypass the build script's question. Reuse the confirmation
through authorized retries that use the same credential.

## 7. Build and verify the actual deliverable

For the combined robot release:

```bash
PL_KIOSK_PASSWORD_CONFIRMED=1 QT_QPA_PLATFORM=offscreen \
  .venv/bin/python -B packaging/robot/release_robot.py build "$TARGET"
```

This runs the gates, validates/reuses exact component archives, builds missing
components, assembles the combined archive, installs it into a disposable root,
and runs the installed launcher with `--self-test`. It does not install onto the
real machine. Allow enough disk space for the bundle, component archives, assembly,
extraction, and temporary installation at the same time.

Expected combined outputs under the combined Git root:

```text
releases/TARGET/robot/RELEASE_VERSION/
    TARGET-robot-RELEASE_VERSION-ARCH.tar.gz
    TARGET-robot-RELEASE_VERSION-ARCH.tar.gz.sha256
    manifest.json
```

For a requested standalone platform installer, use the supported component route:

```bash
PL_KIOSK_PASSWORD_CONFIRMED=1 QT_QPA_PLATFORM=offscreen \
  .venv/bin/python -B packaging/platform/build_and_release.py "$TARGET" "$PLATFORM_VERSION"
```

Set `PLATFORM_VERSION` to the confirmed unused version first. Its installer kits
are under `dist/platform-releases/TARGET/`. Do not pass a standalone archive to a
combined robot updater.

Inspect the final report for the selected target/version/action and archive hash.
Every required stage must pass, including temporary installation and installed
frozen self-test for combined builds. An archive left after a failed stage is not
a verified release. Use the supported `verify` action to retry verification of an
unchanged combined artifact; changed source/payload requires a new version.

For changed external UI dependencies, additionally confirm the frozen archive
contains the tested implementation. A source-only test or local reinstall does
not prove that the frozen bundle contains it.

## 8. Deliver through the authorized route

- **Files only:** retain the verified archive, checksum, manifest and report in a
  durable location. Do not leave the only copy in `/tmp`.
- **LAN update feed:** follow [lan-feed.md](references/lan-feed.md). Advertise the
  release only after verification; retain the previous release for rollback.
- **SVN/GitHub:** follow [publication.md](references/publication.md) and current
  `AGENTS.md`. Building or serving a local test release is not GitHub publication.

Do not change station update keys, providers, channels, calibration, workpieces,
desktop setup, or backend behavior merely to make an update install.

## 9. Hand off the result

Report the target, robot/platform/backend versions and backend profile, artifact
location or verified feed URL, verification result, and any remaining limitation.
Say whether SVN/GitHub publication happened. Give the matching installation steps.

For an existing combined updater: **Check for updates → Download update → Install
after application closes**, then close the application. Do not claim the station
installed the release until that is verified there. Software self-tests are not
physical robot or touchscreen acceptance tests.

Historical deployment/paint-profile context remains in
[handoff.md](references/handoff.md). Its versions, paths and outstanding work are
dated evidence, not current release instructions.
