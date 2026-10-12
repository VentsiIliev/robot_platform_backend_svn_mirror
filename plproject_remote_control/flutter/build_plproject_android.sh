#!/usr/bin/env bash
# Build the PL PROJECT ARM64 Android app with the pinned toolchain.
set -euo pipefail
MODE=${1:-release}
if [[ "$MODE" != release && "$MODE" != debug ]]; then
    echo "Usage: $0 [release|debug]" >&2
    exit 2
fi
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
: "${ANDROID_NDK_HOME:?Set ANDROID_NDK_HOME to NDK r28c}"
: "${VCPKG_ROOT:?Set VCPKG_ROOT to the pinned vcpkg checkout}"
export ANDROID_NDK_ROOT="$ANDROID_NDK_HOME"
for tool in flutter cargo rustup flutter_rust_bridge_codegen; do
    command -v "$tool" >/dev/null || { echo "Missing build tool: $tool" >&2; exit 1; }
done
if [[ ! -f libs/hbb_common/Cargo.toml ]]; then
    echo "Run git submodule update --init --recursive first." >&2
    exit 1
fi
if [[ "$MODE" == release && ! -f flutter/android/key.properties ]]; then
    echo "Configure flutter/android/key.properties for release signing first." >&2
    exit 1
fi
# Apply the pinned Flutter patch once; allow an already-patched SDK.
FLUTTER_SDK=$(cd "$(dirname "$(command -v flutter)")/.." && pwd)
PATCH="$ROOT/.github/patches/flutter_3.24.4_dropdown_menu_enableFilter.diff"
if git -C "$FLUTTER_SDK" apply --check "$PATCH" 2>/dev/null; then
    git -C "$FLUTTER_SDK" apply "$PATCH"
elif ! git -C "$FLUTTER_SDK" apply --reverse --check "$PATCH" 2>/dev/null; then
    echo "Flutter SDK does not match the required 3.24.5 patch." >&2
    exit 1
fi
# Bridge generation runs on the host, before target-specific bindgen arguments.
unset BINDGEN_EXTRA_CLANG_ARGS
(cd flutter && flutter pub get)
flutter_rust_bridge_codegen --rust-input ./src/flutter_ffi.rs \
    --dart-output ./flutter/lib/generated_bridge.dart \
    --c-output ./flutter/ios/Runner/bridge_generated.h
rustup target add aarch64-linux-android
./flutter/build_android_deps.sh arm64-v8a
export BINDGEN_EXTRA_CLANG_ARGS="--target=aarch64-linux-android21 --sysroot=$ANDROID_NDK_HOME/toolchains/llvm/prebuilt/linux-x86_64/sysroot -I$ANDROID_NDK_HOME/toolchains/llvm/prebuilt/linux-x86_64/sysroot/usr/include/aarch64-linux-android"
cargo ndk --platform 21 --target aarch64-linux-android \
    build --locked --lib --release --features flutter,hwcodec
JNI_DIR=flutter/android/app/src/main/jniLibs/arm64-v8a
mkdir -p "$JNI_DIR"
cp target/aarch64-linux-android/release/liblibrustdesk.so "$JNI_DIR/librustdesk.so"
cp "$ANDROID_NDK_HOME/toolchains/llvm/prebuilt/linux-x86_64/sysroot/usr/lib/aarch64-linux-android/libc++_shared.so" "$JNI_DIR/libc++_shared.so"
(cd flutter && flutter build apk "--$MODE" --split-per-abi \
    --target-platform android-arm64 --build-name="${ANDROID_BUILD_NAME:-1.4.9}" \
    --build-number="${ANDROID_BUILD_NUMBER:-68}")
echo "APK: $ROOT/flutter/build/app/outputs/flutter-apk/app-arm64-v8a-$MODE.apk"
