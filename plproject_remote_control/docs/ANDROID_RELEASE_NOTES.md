## PL PROJECT Remote Support — initial Android release

First signed ARM64 Android release based on RustDesk 1.4.9.

### Included

- PL PROJECT name, logo, launcher icons, and purple UI theme
- Branded splash screen, Android notifications, and accessibility service
- Outgoing remote-desktop connections and incoming Android screen sharing/control
- Self-hosted RustDesk OSS ID/relay server support
- Service startup without the inherited scam-warning dialog or countdown
- Android's screen-sharing and accessibility permission approvals

### Installation

Download the ARM64 release APK and allow installation from the source you use
to open it. Requires an ARM64 Android phone/tablet running Android 5.1 or newer.
Verify the download against `SHA256SUMS`.

If you installed the earlier debug APK, uninstall it first: the release uses a
dedicated signing key. This removes saved app settings. Configure your PL PROJECT
ID/relay server address and public key after installation. Future release updates
reuse the release signing key.

### Build documentation

See `ANDROID_BUILD_REQUIREMENTS.md` for the complete build and signing procedure.
The release includes Android only; no iOS IPA is included. The privacy-policy
link is inherited pending a PL PROJECT policy URL.

### License

PL PROJECT Remote Support is a modified RustDesk distribution. See the
repository source and license for the applicable GNU AGPL-3.0 requirements.
