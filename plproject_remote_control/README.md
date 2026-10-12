# PL PROJECT Remote Support

PL PROJECT Remote Support is a customized remote-support client for PL PROJECT
robot systems.

It is based on RustDesk 1.4.9 and is designed to connect PL PROJECT robots
through a self-hosted RustDesk OSS server rather than relying on the public
RustDesk infrastructure.

## Source of truth

This project is maintained in SVN trunk as `plproject_remote_control/`, beside
`platform/` and `backend/`. The current GitHub mirror is
https://github.com/VentsiIliev/robot_platform_backend_svn_mirror.
Publish source changes through SVN before pushing the mirror; see
[SVN import and publication notes](SVN_IMPORT.md). The former standalone GitHub
repository is retained only as historical provenance. Release assets and new
Android builds belong to the mirror. A future GitLab split is not configured yet.

## Purpose

PL PROJECT Remote Support provides remote desktop access to robot computers for
support, diagnostics, commissioning and maintenance.

The Linux client provides:

- Remote viewing and control of the robot's actual desktop
- Unattended remote access
- Self-hosted ID and relay infrastructure
- PL PROJECT branding
- PL PROJECT application and tray icons
- PL PROJECT branded Connection Manager
- Visible active remote-session controls
- Permanent-password support
- Automatic service startup
- Linux system tray integration
- No RustDesk account login requirement

## Architecture

A typical installation consists of:

    Support Laptop
          |
          | Remote connection
          |
          v
    PL PROJECT RustDesk OSS Server
       hbbs + hbbr
          |
          |
          v
    Robot Computer
    PL PROJECT Remote Support

The self-hosted server provides the RustDesk ID and relay services.

Each robot receives its own RustDesk ID and can be configured with an
unattended-access password.

Server addresses, public keys and robot credentials are deployment-specific
and are not stored in this repository.

## Supported Platform

The current PL PROJECT build has been developed and tested for:

- Ubuntu 24.04 LTS
- x86_64 / amd64
- X11 desktop sessions

The generated Linux installer is a Debian package:

    rustdesk-1.4.9.deb

Windows support can be built from the same RustDesk codebase, but the current
documented PL PROJECT build procedure focuses on Linux.

Android ARM64 support is available with PL PROJECT branding. See
[Android build and release instructions](ANDROID_BUILD_REQUIREMENTS.md) for the
pinned toolchain, APK builds, signing, and installation.

## Building

Detailed build requirements and the complete reproducible build procedure are
documented in:

    BUILD_REQUIREMENTS.md

The tested toolchain includes:

- Rust 1.75.0
- Flutter 3.24.5 for the final application
- Flutter 3.22.3 for bridge generation
- flutter_rust_bridge_codegen 1.80.1
- cargo-expand 1.0.95
- pinned vcpkg dependencies

### Build Rust

From the repository root:

    export VCPKG_ROOT="$HOME/src/vcpkg"
    export PATH="$HOME/src/flutter-3.24.5/bin:$HOME/.cargo/bin:$PATH"
    export CARGO_INCREMENTAL=0

    cargo build --locked --lib \
      --features hwcodec,flutter,unix-file-copy-paste \
      --release

### Build Debian package

After the Rust library has been built:

    export DEB_ARCH=amd64

    python3 ./build.py --flutter --skip-cargo

The resulting PL PROJECT Debian package is:

    rustdesk-1.4.9.deb

See `BUILD_REQUIREMENTS.md` for the complete setup procedure.

## Installation

Install the package with:

    sudo systemctl stop rustdesk
    sudo dpkg -i ./rustdesk-1.4.9.deb
    sudo systemctl daemon-reload
    sudo systemctl restart rustdesk

Check the service:

    systemctl status rustdesk

Check the running processes:

    ps -ef | grep '[r]ustdesk'

A normal PL PROJECT Linux installation can contain:

    rustdesk --service
    rustdesk --server
    rustdesk --tray

## Launching the GUI

Launch the desktop application with:

    /usr/bin/rustdesk

The installed product is displayed as:

    PL PROJECT Remote Support

## Robot Configuration

A robot client must be configured to use the PL PROJECT self-hosted RustDesk
server.

Typical configuration requires:

- ID Server address
- Server public key
- Unattended-access password

The relay server can be configured separately when required.

Do not commit deployment passwords, server private keys or customer-specific
credentials to this repository.

## Active Remote Sessions

PL PROJECT Remote Support intentionally keeps the active-session Connection
Manager available during a support session.

This allows someone at the robot to see that a remote session is active and
provides access to session permissions and the Disconnect control.

The system tray is also enabled and uses PL PROJECT branding.

## Account Login

The desktop Account/Login entry is hidden in the PL PROJECT client.

The current PL PROJECT deployment uses RustDesk OSS ID and relay services and
does not require the RustDesk Pro account API for normal robot remote support.

The underlying upstream account implementation has not been removed from the
source code.

## Branding

The customized client includes:

- PL PROJECT Remote Support product name
- PL PROJECT application icon
- PL PROJECT tray icon
- PL PROJECT logo in the Connection Manager
- PL PROJECT purple application theme
- PL PROJECT website
- PL PROJECT Debian package metadata

Some internal RustDesk names are deliberately retained for compatibility,
including the executable and Debian package identifiers.

## Development Branch

PL PROJECT development is performed on:

    plproject-remote-support

The original RustDesk repository can remain configured as the `origin` remote,
while the PL PROJECT repository is configured as `plproject`.

Example:

    git remote -v

Push PL PROJECT changes with:

    git push plproject plproject-remote-support

## Repository Safety

Never commit:

- RustDesk server private keys
- unattended-access passwords
- GitHub access tokens
- SSH private keys
- customer credentials
- API secrets
- robot-specific secrets

Review staged changes before every push:

    git diff --cached --check
    git diff --cached --stat
    git status

## Python Tooling

Small image/resource-generation utilities use Python and Pillow.

Install with:

    python3 -m pip install -r requirements.txt

Python is not the primary application build system. Rust, Flutter and native
Linux dependencies are documented in `BUILD_REQUIREMENTS.md`.

## Upstream Project

PL PROJECT Remote Support is based on the RustDesk open-source project.

The PL PROJECT fork retains upstream code and internal compatibility where
required while adding PL PROJECT-specific branding and deployment behavior.

## License

RustDesk is licensed under the GNU Affero General Public License version 3
(AGPL-3.0).

PL PROJECT Remote Support contains modified RustDesk source code and must be
distributed in accordance with the applicable AGPL requirements.

Distribution of modified binaries may require making the corresponding source
code available to recipients.

PL PROJECT branding does not transfer ownership of upstream RustDesk code, and
legally required upstream copyright and licensing information must be
preserved.

See the repository license files and `BUILD_REQUIREMENTS.md` before distributing
builds to customers.
