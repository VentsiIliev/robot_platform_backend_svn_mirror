#!/usr/bin/env python3
"""Build one robot-system/profile bundle without bundling other systems."""
import argparse
import ast
import os
import shutil
from pathlib import Path
import subprocess
import sys

from targets import ROOT, load_target, prepare_target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", help="Key from config/release_targets.json")
    args = parser.parse_args()
    target = load_target(args.target)
    config_dir = ROOT / "build/platform-config" / args.target
    prepare_target(args.target, config_dir)
    work = ROOT / "build/pyinstaller" / args.target
    environment = dict(os.environ, ROBOT_PLATFORM_BUILD_TARGET=args.target)
    environment["MPLCONFIGDIR"] = str(work / "matplotlib")
    Path(environment["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
                    "--distpath", str(ROOT / "dist"), "--workpath", str(work),
                    "packaging/platform.spec"], cwd=ROOT, env=environment, check=True)
    toc = ast.literal_eval((work / "platform/PYZ-00.toc").read_text())
    # PYZ entries are nested; inspect module-name tuples rather than source paths.
    def modules(value):
        if isinstance(value, (tuple, list)):
            if value and isinstance(value[0], str):
                yield value[0]
            for item in value:
                yield from modules(item)
    allowed = set(target["packages"])
    for module in modules(toc):
        parts = module.split(".")
        if parts[:2] == ["src", "robot_systems"] and len(parts) > 3 and parts[2] not in allowed:
            raise RuntimeError(f"Other robot system bundled: {module}")
        if parts[:2] == ["src", "robot_systems"] and "example_usage" in parts:
            raise RuntimeError(f"Development example bundled: {module}")
    bundle = ROOT / "dist" / target["product"]
    support = [sys.executable, "packaging/remote_support/build_payload.py", str(bundle / "installation/remote-support")]
    if os.environ.get("PL_SUPPORT_VENDOR_INSTALLER"):
        support += ["--vendor-installer", os.environ["PL_SUPPORT_VENDOR_INSTALLER"]]
    subprocess.run(support, cwd=ROOT, check=True)
    # The combined robot release bypasses build_release.py. Include its shared
    # first-install provisioning entry point directly in the platform bundle.
    installation = bundle / "installation"
    (installation / "kiosk").mkdir(exist_ok=True)
    shutil.copy2(ROOT / "setup_kiosk.sh", installation / "kiosk/setup_kiosk.sh")
    shutil.copy2(ROOT / "packaging/platform/manage.py", installation / "system-setup.py")
    shutil.copytree(ROOT / "src/engine/updates", installation / "src/engine/updates",
                    ignore=shutil.ignore_patterns("__pycache__"), dirs_exist_ok=True)
    for name in ("src/__init__.py", "src/engine/__init__.py"):
        shutil.copy2(ROOT / name, installation / name)
    updater = installation / 'updater'
    updater.mkdir(exist_ok=True)
    shutil.copy2(ROOT / 'packaging/platform/manage.py', updater / 'manage.py')
    shutil.copytree(installation / 'src', updater / 'src', dirs_exist_ok=True)
    print(f"{args.target} bundle created at: {bundle}")


if __name__ == "__main__":
    main()
