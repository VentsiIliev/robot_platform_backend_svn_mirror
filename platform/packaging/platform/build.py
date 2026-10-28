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

DEFAULT_KIOSK_PASSWORD_FILE = Path.home() / ".config/pl-project/kiosk-password.json"


def confirm_kiosk_password(password_source):
    """Require an explicit choice before embedding a credential in a release."""
    if not sys.stdin.isatty():
        if os.environ.get("PL_KIOSK_PASSWORD_CONFIRMED") == "1":
            return
        raise RuntimeError(
            "Non-interactive build requires PL_KIOSK_PASSWORD_CONFIRMED=1 after "
            "the kiosk password hash has been reviewed."
        )
    while True:
        answer = input(
            f"Kiosk password hash: {password_source}\n"
            "Is this password set and ready for this release? "
            "[u]se / [c]hange / [q]uit: "
        ).strip().lower()
        if answer in {"u", "use"}:
            return
        if answer in {"c", "change"}:
            from src.bootstrap.kiosk_password import main as set_kiosk_password
            set_kiosk_password(["--file", str(password_source)])
            continue
        if answer in {"", "q", "quit"}:
            raise RuntimeError("Build cancelled before packaging the kiosk password hash")
        print("Choose 'u', 'c', or 'q'.")


def prepare_kiosk_password():
    """Resolve, validate and confirm the shared production credential hash."""
    configured = os.environ.get("PL_KIOSK_PASSWORD_FILE")
    password_source = Path(configured).expanduser() if configured else DEFAULT_KIOSK_PASSWORD_FILE
    password_source = password_source.resolve()
    if not password_source.is_file():
        raise RuntimeError(
            "Shared kiosk password hash is required. Create "
            f"{DEFAULT_KIOSK_PASSWORD_FILE} or set PL_KIOSK_PASSWORD_FILE."
        )
    sys.path.insert(0, str(ROOT))
    from src.bootstrap.kiosk_password import KioskPassword
    KioskPassword(password_source)
    confirm_kiosk_password(password_source)
    # Revalidate after the optional interactive rotation.
    KioskPassword(password_source)
    return password_source


def stage_kiosk_password(destination, password_source=None):
    """Embed the already reviewed shared production credential hash."""
    password_source = password_source or prepare_kiosk_password()
    shutil.copy2(password_source, destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", help="Key from config/release_targets.json")
    args = parser.parse_args()
    kiosk_password = prepare_kiosk_password()
    target = load_target(args.target)
    config_dir = ROOT / "build/platform-config" / args.target
    prepare_target(args.target, config_dir)
    work = ROOT / "build/pyinstaller" / args.target
    environment = dict(os.environ, ROBOT_PLATFORM_BUILD_TARGET=args.target)
    environment["MPLCONFIGDIR"] = str(work / "matplotlib")
    Path(environment["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
                    "--distpath", str(ROOT / "dist"), "--workpath", str(work),
                    "packaging/platform/platform.spec"], cwd=ROOT, env=environment, check=True)
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
    subprocess.run([sys.executable, "packaging/accounts/build_payload.py",
                    str(installation / "account-maintenance")], cwd=ROOT, check=True)
    (installation / "kiosk").mkdir(exist_ok=True)
    shutil.copy2(ROOT / "packaging/kiosk/setup_kiosk.sh", installation / "kiosk/setup_kiosk.sh")
    stage_kiosk_password(installation / "kiosk/kiosk-password.json", kiosk_password)
    shutil.copy2(ROOT / "packaging/runtime/manage.py", installation / "system-setup.py")
    shutil.copytree(ROOT / "src/engine/updates", installation / "src/engine/updates",
                    ignore=shutil.ignore_patterns("__pycache__"), dirs_exist_ok=True)
    (installation / "src/engine/core").mkdir(parents=True, exist_ok=True)
    for name in ("src/engine/core/__init__.py", "src/engine/core/durable_files.py"):
        shutil.copy2(ROOT / name, installation / name)
    for name in ("src/__init__.py", "src/engine/__init__.py"):
        shutil.copy2(ROOT / name, installation / name)
    updater = installation / 'updater'
    updater.mkdir(exist_ok=True)
    shutil.copy2(ROOT / 'packaging/runtime/manage.py', updater / 'manage.py')
    shutil.copytree(installation / 'src', updater / 'src', dirs_exist_ok=True)
    print(f"{args.target} bundle created at: {bundle}")


if __name__ == "__main__":
    main()
