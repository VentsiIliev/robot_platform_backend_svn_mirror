# PL PROJECT Remote Support — Android build and release

The initial Android release targets ARM64 (`arm64-v8a`) devices running Android
5.1/API 22 or newer. Package ID: `net.plproject.remote_support`. The base app
version is 1.4.9; the initial release version code is 2068. Desktop build
instructions remain in [BUILD_REQUIREMENTS.md](BUILD_REQUIREMENTS.md).

## Tested toolchain

- Ubuntu 24.04 x86_64
- Flutter 3.24.5 / Dart 3.5.4
- Rust 1.75.0 with the `aarch64-linux-android` target
- Java 17
- Android SDK platform 34 and build-tools 34.0.0 (Gradle also installs plugin SDKs)
- Android NDK r28c: `28.2.13676358`
- vcpkg commit `120deac3062162151622ca4860575a33844ba10b`
- cargo-ndk 3.1.2, cargo-expand 1.0.95, flutter_rust_bridge_codegen 1.80.1

## Install host tools

```sh
sudo apt-get update
sudo apt-get install -y build-essential clang libclang-dev cmake curl git \
  unzip xz-utils pkg-config nasm ninja-build perl openjdk-17-jdk-headless
```

Install Rust using rustup, then install the pinned tools:

```sh
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs -o /tmp/rustup-init.sh
sh /tmp/rustup-init.sh -y --default-toolchain 1.75.0
. "$HOME/.cargo/env"
rustup target add aarch64-linux-android
cargo install cargo-ndk --version 3.1.2 --locked
cargo install cargo-expand --version 1.0.95 --locked
cargo install flutter_rust_bridge_codegen --version 1.80.1 --features uuid --locked
```

## Install Flutter, Android SDK, and vcpkg

Use a persistent tool directory rather than `/tmp`:

```sh
export PLPROJECT_BUILD_ROOT="$HOME/plproject-build-tools"
mkdir -p "$PLPROJECT_BUILD_ROOT"
cd "$PLPROJECT_BUILD_ROOT"
curl -fL https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.24.5-stable.tar.xz -o flutter.tar.xz
printf '%s  %s\n' a7c82f551a9eae018e078f6bb186171e5a77920d35a3d75a61d9a593d0a9e4ae flutter.tar.xz | sha256sum -c -
tar -xf flutter.tar.xz
export PATH="$PLPROJECT_BUILD_ROOT/flutter/bin:$HOME/.cargo/bin:$PATH"
flutter --disable-analytics

curl -fL https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip -o android-tools.zip
unzip -q android-tools.zip -d android-tools
mkdir -p android-sdk/cmdline-tools
mv android-tools/cmdline-tools android-sdk/cmdline-tools/latest
export ANDROID_HOME="$PLPROJECT_BUILD_ROOT/android-sdk"
export ANDROID_SDK_ROOT="$ANDROID_HOME"
"$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager" --licenses
"$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager" \
  'platform-tools' 'platforms;android-34' 'build-tools;34.0.0' 'ndk;28.2.13676358'
export ANDROID_NDK_HOME="$ANDROID_HOME/ndk/28.2.13676358"
export ANDROID_NDK_ROOT="$ANDROID_NDK_HOME"
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH="$JAVA_HOME/bin:$ANDROID_HOME/platform-tools:$PATH"

git clone https://github.com/microsoft/vcpkg.git "$PLPROJECT_BUILD_ROOT/vcpkg"
git -C "$PLPROJECT_BUILD_ROOT/vcpkg" checkout 120deac3062162151622ca4860575a33844ba10b
"$PLPROJECT_BUILD_ROOT/vcpkg/bootstrap-vcpkg.sh" -disableMetrics
export VCPKG_ROOT="$PLPROJECT_BUILD_ROOT/vcpkg"
export VCPKG_MAX_CONCURRENCY=4
# Adjust to the installed LLVM version if necessary.
export LIBCLANG_PATH=/usr/lib/llvm-18/lib
```

Keep these exports in a local environment file and load it before each build.
The build script currently supports a Linux x86_64 host and ARM64 Android only.

## Clone and build

```sh
git clone https://github.com/VentsiIliev/robot_platform_backend_svn_mirror.git
cd robot_platform_backend_svn_mirror/plproject_remote_control
# For an existing checkout:
git submodule update --init --recursive
./flutter/build_plproject_android.sh debug
```

The script patches Flutter once, resolves Dart dependencies, generates the
Flutter/Rust bindings, builds native media dependencies, compiles the Rust
library, copies both Rust and C++ shared libraries, and packages the APK.
The first build downloads several gigabytes and compiles native codecs.
Subsequent builds reuse caches. `flutter pub get` may change `pubspec.lock`
because the desktop and Android toolchains resolve different SDK dependencies;
review that change before committing it.

Debug APK: `flutter/build/app/outputs/flutter-apk/app-arm64-v8a-debug.apk`.

## Release signing

Use a dedicated signing key and back it up securely. All future releases must
reuse the same key. Do not commit the key, its passwords, or `key.properties`.

Create a key interactively (passwords are not included in shell arguments):

```sh
mkdir -p .local/android-signing
chmod 700 .local/android-signing
keytool -genkeypair -storetype JKS \
  -keystore "$PWD/.local/android-signing/plproject-android-release.jks" \
  -alias plproject -keyalg RSA -keysize 3072 -validity 10000 \
  -dname 'CN=PL PROJECT Remote Support, O=PL PROJECT'
```

Create `flutter/android/key.properties` with your local values:

```properties
storeFile=/absolute/path/to/plproject-android-release.jks
keyAlias=plproject
storePassword=YOUR_STORE_PASSWORD
keyPassword=YOUR_KEY_PASSWORD
```

```sh
chmod 600 flutter/android/key.properties .local/android-signing/*.jks
./flutter/build_plproject_android.sh release
```

Release APK: `flutter/build/app/outputs/flutter-apk/app-arm64-v8a-release.apk`.
The default build number is 68; Flutter adds 2000 for the ARM64 split, giving
release version code 2068. Increment `ANDROID_BUILD_NUMBER` for
subsequent releases. `ANDROID_BUILD_NAME` defaults to 1.4.9.

For a Flutter-only rebuild after native libraries and bindings are ready:

```sh
cd flutter
flutter build apk --release --split-per-abi --target-platform android-arm64 \
  --build-name=1.4.9 --build-number=68
```

## Verify and install

```sh
"$ANDROID_HOME/build-tools/34.0.0/apksigner" verify --verbose \
  flutter/build/app/outputs/flutter-apk/app-arm64-v8a-release.apk
adb install -r flutter/build/app/outputs/flutter-apk/app-arm64-v8a-release.apk
```

The initial release key differs from the earlier debug test key. Uninstall the
debug app before installing the release APK; uninstalling removes its saved
settings. Enter your self-hosted ID/relay server address and public key again.
Future release APKs signed with the same key can update the installed app.

Check the PL PROJECT launcher and splash screen, outgoing desktop connections,
and Android incoming screen sharing/Input Control. The inherited scam-warning
dialog is removed; Android screen-capture and accessibility approvals remain.
The privacy-policy link still points to the inherited RustDesk policy pending a
PL PROJECT policy URL. iOS branding is present, but this release includes no IPA.

## GitHub publishing

The Android tag format is `v1.4.9-plproject.android.1`. It does not change the
existing desktop release or tag. The Android publishing workflow requires these
mirror repository Actions secrets:

- `ANDROID_RELEASE_KEYSTORE_BASE64`: base64-encoded dedicated JKS file
- `ANDROID_RELEASE_STORE_PASSWORD`
- `ANDROID_RELEASE_KEY_PASSWORD`
- `ANDROID_RELEASE_KEY_ALIAS`: `plproject`

Use `python3 res/configure_android_release_secrets.py` after authenticating
GitHub CLI. This reads the local initial-release credentials without printing
them. It requires write access to this repository's Actions secrets.

Publish changes through SVN and the GitHub mirror using the enclosing platform publication script, then push the Android tag to the mirror. The
workflow builds a signed ARM64 release APK, verifies its signature, and publishes
it together with `SHA256SUMS` and platform-specific release notes. It fails
before building if signing secrets are missing. Keep an independent backup of
the key and credentials; GitHub secrets cannot be downloaded to recover them.
