"""Stage the independent support installer for a product release bundle."""

import argparse
import shutil
from pathlib import Path


def build_payload(destination: Path, vendor_installer: Path | None = None) -> None:
    source = Path(__file__).resolve().parent
    vendor_installer = vendor_installer or source / "install_pl_remote_support.sh"
    if "--provision-only" not in vendor_installer.read_text():
        raise ValueError("Vendor installer must support --provision-only")
    destination.mkdir(parents=True, exist_ok=True)
    for name in ("install.sh", "README.md", "update_package.py", "install_update_helper.sh"):
        shutil.copy2(source / name, destination / name)
    config = vendor_installer.with_name("release.conf")
    if not config.is_file():
        config = source / "release.conf"
    shutil.copy2(config, destination / "release.conf")
    shutil.copy2(source.parent / "kiosk/auto_login.sh", destination / "auto_login.sh")
    shutil.copy2(vendor_installer, destination / "install_pl_remote_support.sh")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--vendor-installer", type=Path)
    args = parser.parse_args()
    build_payload(args.destination, args.vendor_installer)
