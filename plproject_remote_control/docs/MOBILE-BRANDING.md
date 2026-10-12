# PL PROJECT mobile apps

Android and iOS use the existing desktop PL PROJECT logo and app icon, the
shared purple Flutter theme (`#7B2CE3`), and the name
**PL PROJECT Remote Support**. Native launcher icons, launch screens, Android
notifications, accessibility labels, and the floating control icon are branded.

- Android application ID: `net.plproject.remote_support`
- iOS bundle ID: `net.plproject.remoteSupport`
- Connection links: `plproject://` and the existing `rustdesk://` scheme

The Android Kotlin/manifest namespace remains `com.carriez.flutter_hbb` for
native compatibility. Manifest components have fully qualified class names;
the installed application uses the new PL PROJECT ID. Existing RustDesk
installations therefore do not share app storage with this app.

## Regenerating artwork

From the repository root, with Pillow installed:

```sh
python3 res/generate_mobile_branding.py
```

The script resizes `flutter/assets/pl_project_app_icon.png` and
`flutter/assets/pl_project_logo.png`. iOS icons have an opaque white background;
Android notification icons use a white silhouette on transparency. Generated
native images are included in version control.

## Building and testing

Use the native dependency/Rust library build steps in
`.github/workflows/flutter-build.yml` before building the Flutter app. Flutter
alone cannot build the missing native libraries. Initialize the repository
submodules, install the Flutter version used by that workflow, and generate the
Flutter/Rust bridge files as required by the workflow.

For Android, install Java, Android SDK/NDK, and the vcpkg dependencies, build and
copy `librustdesk.so` to each required `flutter/android/app/src/main/jniLibs/`
ABI directory. For a debug test build, run `flutter build apk --debug` from
`flutter/`. A release build additionally needs your own signing configuration
in `flutter/android/key.properties`.

For iOS, use macOS/Xcode and CocoaPods, build the iOS Rust library, then select
your Apple development team and provisioning profile for
`net.plproject.remoteSupport` in Xcode. Use your own signing credentials to
install on a physical iPhone/iPad.

Check launcher icons, splash screens in light/dark mode, the app header,
settings, and a connection to your configured server. On Android also check
the notification and floating menu, then enable **PL PROJECT Input** in system
Accessibility settings and test incoming screen sharing and input control.
iOS supports outgoing remote connections; incoming control is not provided by
this codebase.

The existing RustDesk privacy-policy link is retained pending a PL PROJECT
policy URL. Upstream source references and native library names are retained.
The unused upstream GoogleService plist is not a configured PL PROJECT Firebase
project; Firebase initialization is commented out in this application.

## Validation in this workspace

Android resource XML and native component resolution, iOS plist/storyboard,
all icon catalog entries, image sizes, notification silhouettes, iOS icon
opacity, and `git diff --check` were validated.

An ARM64 Android debug APK was built successfully with Flutter 3.24.5,
Rust 1.75.0, Java 17, and NDK r28c. Its signing, package identity, ZIP
integrity, and bundled Rust/C++ libraries were verified. Artifact:
`flutter/build/app/outputs/flutter-apk/app-arm64-v8a-debug.apk`.
It uses Android application ID `net.plproject.remote_support`, version
`1.4.9` (2067), and Android API 22 or newer. Device behavior still needs testing.
No iOS build was performed.

The toolchains, dependency builds, and logs are in
`/tmp/plproject-android-build`. They are temporary. While they remain available,
rebuild from `flutter/` with:

```sh
. /tmp/plproject-android-build/env.sh
flutter build apk --debug --split-per-abi --target-platform android-arm64
```

For native compilation, the build environment supplies Android NDK sysroot
arguments through `BINDGEN_EXTRA_CLANG_ARGS`. Both `librustdesk.so` and the NDK's
`libc++_shared.so` must be copied into the ARM64 `jniLibs` directory before
packaging. This APK is signed with a debug key for device testing.

The inherited scam-warning dialog and countdown have been removed from both
Android service-start controls. Android screen-capture approval and the Input
Control accessibility permission flow remain in place.

For the initial signed Android release and complete reproducible build steps,
see [ANDROID_BUILD_REQUIREMENTS.md](../ANDROID_BUILD_REQUIREMENTS.md). The
end-to-end script `flutter/build_plproject_android.sh release` was validated
with the prepared toolchain; signing and native-library packaging checks passed.
