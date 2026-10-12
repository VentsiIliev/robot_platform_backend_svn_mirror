# PL PROJECT remote control in SVN

This directory contains the PL PROJECT branded RustDesk source from
https://github.com/VentsiIliev/plproject_remote_support, alongside `platform/`
and `backend/` in SVN trunk. `SVN_IMPORT.json` records the source branch, commit
and dependency revision used for this import.

The `libs/hbb_common` Git submodule is included as ordinary versioned files so
SVN checkouts and GitHub mirror clones contain the complete source. There are no
nested Git repositories. The original `.gitmodules` file is retained as upstream
reference; the enclosing repository does not use Git submodules for this folder.
The original project history remains in the source GitHub repository; SVN records
this source snapshot and subsequent changes.

## Build and releases

Run the original build commands from this directory, not the enclosing repository
root. Follow `BUILD_REQUIREMENTS.md` and `ANDROID_BUILD_REQUIREMENTS.md`; replace
any example `~/src/rustdesk` path with your checkout's `plproject_remote_control`
path. Native dependencies and the pinned Rust, Flutter and vcpkg toolchains are
still required. Existing licences and project documentation are preserved.

SVN trunk is the authoritative source, mirrored to
`VentsiIliev/robot_platform_backend_svn_mirror`. The previous
`plproject_remote_support` repository is historical provenance, not an active
source or release destination. Future GitLab separation is not configured yet.

The PL PROJECT Android workflow is installed at the enclosing repository's
`.github/workflows/plproject-android-release.yml`, with its working directory set
to this folder. Configure Android signing secrets in the mirror before building
new Android releases; GitHub does not transfer secrets between repositories.
Other inherited workflows remain under this folder as upstream reference only.

The enclosing release-import workflow copies the existing Linux and Android
release assets into the mirror, validating the SHA-256 values recorded in
`release-import.json`. Source provenance stays recorded in `SVN_IMPORT.json`.

## Publish changes

Work in the enclosing git-svn checkout's `master` work branch and publish via:

```bash
python3 platform/scripts/publish_changes.py -m "Describe remote control changes" plproject_remote_control
```

This commits, publishes to SVN, and then pushes the SVN-generated history to
`github-svn-mirror` (`VentsiIliev/robot_platform_backend_svn_mirror`). For already
committed changes or publication retries use `--resume`. Do not push pre-dcommit
history, publish this folder as a submodule, or copy nested `.git` directories.
