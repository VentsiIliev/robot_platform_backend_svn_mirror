# PL PROJECT Remote Support — Build Requirements

PL PROJECT Remote Support is a customized build of RustDesk 1.4.9 for
PL PROJECT robot remote-support systems.

This document records the Linux build environment and procedure successfully
used to build the PL PROJECT branded Debian package.

---

## 1. Tested Build Environment

The current Linux build has been tested with:

- Ubuntu 24.04 LTS x86_64
- RustDesk base version: 1.4.9
- Rust toolchain: 1.75.0
- Flutter final build SDK: 3.24.5
- Dart final build version: 3.5.4
- Flutter bridge-generation SDK: 3.22.3
- flutter_rust_bridge_codegen: 1.80.1
- cargo-expand: 1.0.95
- vcpkg commit: `120deac3062162151622ca4860575a33844ba10b`

The PL PROJECT development repository is expected at:

    ~/src/rustdesk

The examples below assume that location.

---

## 2. Ubuntu Build Dependencies

Update the package index:

    sudo apt update

Install the native build tools and development libraries:

    sudo apt install -y \
      build-essential \
      clang \
      cmake \
      curl \
      git \
      wget \
      pkg-config \
      nasm \
      yasm \
      ninja-build \
      rpm \
      xz-utils \
      libgtk-3-dev \
      libxcb-randr0-dev \
      libxcb-shape0-dev \
      libxcb-xfixes0-dev \
      libxcb-xkb-dev \
      libxdo-dev \
      libxfixes-dev \
      libasound2-dev \
      libpulse-dev \
      libayatana-appindicator3-dev \
      libclang-dev \
      libgstreamer1.0-dev \
      libgstreamer-plugins-base1.0-dev \
      libpam0g-dev \
      libva-dev \
      libssl-dev

Package names can vary slightly between Ubuntu releases.

---

## 3. Rust Toolchain

Install Rust using rustup if it is not already installed.

Install the Rust version used by RustDesk 1.4.9:

    rustup toolchain install 1.75.0

Set the repository-specific Rust version:

    cd ~/src/rustdesk
    rustup override set 1.75.0

Verify:

    rustc --version
    cargo --version

Both should report version 1.75.0.

### Rust build utilities

Install the versions used by the RustDesk 1.4.9 workflow:

    cargo install cargo-expand --version 1.0.95 --locked

    cargo install flutter_rust_bridge_codegen \
      --version 1.80.1 \
      --locked

---

## 4. Flutter SDKs

Two Flutter SDK versions are used.

### Flutter 3.24.5 — final application build

The final Linux application is built using Flutter 3.24.5.

Tested versions:

- Framework: `dec2ee5c1f`
- Engine: `a18df97ca5`
- Dart: 3.5.4

The expected location is:

    ~/src/flutter-3.24.5

Set it in PATH with:

    export PATH="$HOME/src/flutter-3.24.5/bin:$HOME/.cargo/bin:$PATH"

Verify:

    flutter --version
    flutter doctor

### Flutter compatibility patch

RustDesk 1.4.9 requires the supplied dropdown-menu patch when using this
Flutter version.

The patch is located in the RustDesk repository:

    .github/patches/flutter_3.24.4_dropdown_menu_enableFilter.diff

Apply it to the Flutter 3.24.5 SDK:

    cd ~/src/flutter-3.24.5

    git apply \
      ~/src/rustdesk/.github/patches/flutter_3.24.4_dropdown_menu_enableFilter.diff

The Flutter SDK will then intentionally contain a modified
`dropdown_menu.dart`.

Do not arbitrarily upgrade the Flutter SDK without retesting the build.

### Flutter 3.22.3 — bridge generation

Flutter 3.22.3 is used specifically for Rust/Flutter bridge generation.

Tested versions:

- Framework: `b0850beeb2`
- Engine: `235db911ba`
- Dart: 3.4.4

Expected location:

    ~/src/flutter-3.22.3

This version matches the bridge-generation configuration used by
RustDesk 1.4.9.

---

## 5. vcpkg

The tested vcpkg revision is:

    120deac3062162151622ca4860575a33844ba10b

Example setup:

    cd ~/src

    git clone https://github.com/microsoft/vcpkg.git

    cd vcpkg

    git checkout 120deac3062162151622ca4860575a33844ba10b

    ./bootstrap-vcpkg.sh

Set the environment variable:

    export VCPKG_ROOT="$HOME/src/vcpkg"

The tested x64-linux environment includes RustDesk native multimedia
dependencies such as:

- AOM
- FFmpeg 7.1
- libjpeg-turbo
- libvpx
- libyuv
- MFX dispatch
- Opus
- AMD AMF
- FFmpeg NV codec headers

Do not arbitrarily update the vcpkg revision or these dependencies without
retesting the RustDesk 1.4.9 build.

---

## 6. Generate the Rust/Flutter Bridge

The generated Rust/Flutter bridge files are required before the Rust library
can be compiled.

Use Flutter 3.22.3:

    cd ~/src/rustdesk

    export PATH="$HOME/src/flutter-3.22.3/bin:$HOME/.cargo/bin:$PATH"

For the bridge-generation step, the `extended_text` dependency may need to
be temporarily changed in:

    flutter/pubspec.yaml

from:

    extended_text: 14.0.0

to:

    extended_text: 13.0.0

Back up the file first:

    cp flutter/pubspec.yaml flutter/pubspec.yaml.bridge-backup

Then:

    cd flutter
    flutter pub get
    cd ..

Generate the bridge:

    flutter_rust_bridge_codegen \
      --rust-input ./src/flutter_ffi.rs \
      --dart-output ./flutter/lib/generated_bridge.dart \
      --c-output ./flutter/macos/Runner/bridge_generated.h

Copy the generated C header for iOS:

    cp ./flutter/macos/Runner/bridge_generated.h \
       ./flutter/ios/Runner/bridge_generated.h

After bridge generation, restore the original dependency file:

    mv flutter/pubspec.yaml.bridge-backup flutter/pubspec.yaml

The generated bridge files are ignored by Git and therefore may need to be
generated on a fresh development machine.

---

## 7. Build the Rust Library

Switch back to Flutter 3.24.5:

    cd ~/src/rustdesk

    export VCPKG_ROOT="$HOME/src/vcpkg"
    export PATH="$HOME/src/flutter-3.24.5/bin:$HOME/.cargo/bin:$PATH"
    export CARGO_INCREMENTAL=0

Build the release Rust library:

    cargo build --locked --lib \
      --features hwcodec,flutter,unix-file-copy-paste \
      --release

A successful build ends with output similar to:

    Finished release [optimized] target(s)

The generated Rust libraries are placed under:

    target/release/

This step must be repeated whenever Rust source code affecting the application
is changed.

---

## 8. Build the Debian Package

After the Rust library has been successfully built:

    cd ~/src/rustdesk

    export VCPKG_ROOT="$HOME/src/vcpkg"
    export PATH="$HOME/src/flutter-3.24.5/bin:$HOME/.cargo/bin:$PATH"
    export CARGO_INCREMENTAL=0
    export DEB_ARCH=amd64

Build the Flutter application and Debian package:

    python3 ./build.py --flutter --skip-cargo

Successful output includes:

    Building Linux application...
    Built build/linux/x64/release/bundle/rustdesk
    dpkg-deb: building package 'rustdesk' in 'rustdesk.deb'.

The build currently may also print:

    rm: cannot remove 'tmpdeb/usr/bin/rustdesk': No such file or directory

This warning has not prevented successful package generation.

The PL PROJECT package used for installation is:

    rustdesk-1.4.9.deb

---

## 9. Rebuilding After Source Changes

### Flutter/Dart or image/resource changes only

If only Flutter UI code, branding, icons, desktop files, or other packaged
resources were changed, the existing Rust release library can normally be
reused.

Run:

    export VCPKG_ROOT="$HOME/src/vcpkg"
    export PATH="$HOME/src/flutter-3.24.5/bin:$HOME/.cargo/bin:$PATH"
    export CARGO_INCREMENTAL=0
    export DEB_ARCH=amd64

    python3 ./build.py --flutter --skip-cargo

### Rust source changes

If Rust source code was changed, first run:

    cargo build --locked --lib \
      --features hwcodec,flutter,unix-file-copy-paste \
      --release

Then package it:

    python3 ./build.py --flutter --skip-cargo

Do not use an old Rust release library after changing Rust source code.

---

## 10. Install the Debian Package

Stop the currently running service:

    sudo systemctl stop rustdesk

Install or upgrade the package:

    sudo dpkg -i ./rustdesk-1.4.9.deb

Reload systemd and start the service:

    sudo systemctl daemon-reload
    sudo systemctl restart rustdesk

Check the service:

    systemctl status rustdesk

Check the running processes:

    ps -ef | grep '[r]ustdesk'

A normal Linux installation can contain processes such as:

    rustdesk --service
    rustdesk --server
    rustdesk --tray

The PL PROJECT build intentionally uses a branded tray icon.

---

## 11. Launch the Desktop GUI

Launch manually with:

    /usr/bin/rustdesk

If an older GUI instance is already running after installing a new build,
close it before evaluating UI changes.

For development testing it can be restarted with:

    pkill -x rustdesk

followed by:

    /usr/bin/rustdesk

Be aware that killing all RustDesk processes during a remote session can
terminate that session.

---

## 12. PL PROJECT Branding

The customized Linux build includes:

- PL PROJECT Remote Support product name
- PL PROJECT application icons
- PL PROJECT tray icon
- PL PROJECT purple application theme
- PL PROJECT Connection Manager branding
- PL PROJECT website
- PL PROJECT Debian package metadata
- Account/Login hidden from the desktop Settings UI for the OSS deployment

Internal RustDesk identifiers such as the executable name, package name,
protocol handlers, configuration identifiers, and some internal application
identifiers have intentionally been retained where changing them could affect
compatibility.

---

## 13. Self-Hosted Server

PL PROJECT Remote Support is designed to work with a self-hosted RustDesk OSS
server.

The OSS server provides the ID and relay infrastructure required for remote
connections.

The Account/Login UI is hidden in the PL PROJECT desktop client because the
PL PROJECT OSS deployment does not use the RustDesk Pro account API.

Server addresses and public keys are deployment-specific and should not be
hard-coded into public documentation if they belong to a private installation.

Never commit server private keys, unattended-access passwords, credentials,
tokens, or other secrets to the repository.

---

## 14. Git Workflow

The upstream RustDesk repository is retained as:

    origin

The PL PROJECT repository can be configured as:

    plproject

Example:

    git remote -v

Development takes place on:

    plproject-remote-support

Before committing changes:

    dart format \
      flutter/lib/common.dart \
      flutter/lib/desktop/pages/desktop_setting_page.dart \
      flutter/lib/desktop/pages/server_page.dart \
      flutter/lib/desktop/widgets/tabbar_widget.dart

    git diff --check

Review changes:

    git status
    git diff

Push the PL PROJECT branch with:

    git push plproject plproject-remote-support

---

## 15. Security

Do not commit any of the following:

- RustDesk server private keys
- unattended-access passwords
- GitHub tokens
- SSH private keys
- API credentials
- customer credentials
- robot-specific secrets

Public RustDesk server keys may be distributed to clients where required, but
private server keys must remain private.

---

## 16. Licensing

PL PROJECT Remote Support is a modified version of RustDesk.

RustDesk is licensed under the GNU Affero General Public License version 3
(AGPL-3.0).

Distribution of modified binaries must comply with the applicable AGPL
requirements, including making the corresponding source code available where
required.

PL PROJECT branding does not transfer ownership of upstream RustDesk code.

Do not falsify or remove legally required upstream copyright or license
information.

Before distributing PL PROJECT Remote Support to customers, review the
repository's license files and ensure that the distributed binaries,
corresponding source code, notices, and license information satisfy the
applicable open-source license requirements.
