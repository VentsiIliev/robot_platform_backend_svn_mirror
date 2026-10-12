#!/usr/bin/env python3
"""Install local Android signing credentials as GitHub Actions secrets."""
import base64
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
folder = root / ".local/android-signing"
credentials = json.loads((folder / "credentials.json").read_text())
values = {
    "ANDROID_RELEASE_KEYSTORE_BASE64": base64.b64encode(
        (folder / "plproject-android-release.jks").read_bytes()).decode(),
    "ANDROID_RELEASE_STORE_PASSWORD": credentials["storePassword"],
    "ANDROID_RELEASE_KEY_PASSWORD": credentials["keyPassword"],
    "ANDROID_RELEASE_KEY_ALIAS": credentials["keyAlias"],
}
for name, value in values.items():
    subprocess.run(["gh", "secret", "set", name, "--repo",
                    "VentsiIliev/robot_platform_backend_svn_mirror"],
                   input=value, text=True, check=True)
    print(f"Configured {name}")
