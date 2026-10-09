#!/usr/bin/env python3
"""Independent installer/updater/launcher. Uses Ubuntu's system Python, not Qt."""
import argparse
import json
import os
import pwd
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import uuid

# Source checkout: parents[2]. Installed tools: this script's directory.
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE if (HERE / "src").is_dir() else HERE.parents[1]))
from src.engine.updates.config import UpdateConfig, default_config_path, default_install_root
from src.engine.updates.files import atomic_json, lock, sync_tree, sync_directory
from src.engine.updates.updater import PlatformUpdater
from src.engine.updates.service_install import install_service
from src.engine.updates.releases import validate_manifest, release_executable
from src.engine.updates.environment import subprocess_environment


def desktop_user():
    """Identify the desktop account even when invoked through sudo."""
    user = pwd.getpwuid(os.getuid()).pw_name
    if os.geteuid() == 0:
        user = os.environ.get("SUDO_USER", "")
        if not user or user == "root":
            raise RuntimeError("Run the platform installer as the desktop user")
    return user


def install_remote_support(root):
    """Install SSH and enable branded remote support at boot."""
    payload = root / "current/platform/installation/remote-support"
    installer = payload / "install.sh"
    vendor = payload / "install_pl_remote_support.sh"
    if not installer.is_file() or not vendor.is_file():
        raise RuntimeError("Platform installed, but remote-support payload is missing; rebuild this release")
    ui_user = desktop_user()
    command = ["bash", str(installer), ui_user, "--vendor-installer", str(vendor)]
    if os.geteuid() != 0:
        command.insert(0, "sudo")
    print("Installing remote support (administrator authentication may be required)...", flush=True)
    try:
        subprocess.run(command, check=True)
    except (OSError, subprocess.CalledProcessError) as error:
        raise RuntimeError("Platform installed, but remote-support installation failed; rerun the installer to retry: " + str(error)) from error


def install_kiosk(root, config_path, mode, launcher=None):
    """Launch through the stable updater path so kiosk follows future releases."""
    if mode == "off":
        return
    installer = root / "current/platform/installation/kiosk/setup_kiosk.sh"
    if not installer.is_file():
        raise RuntimeError("Kiosk payload is missing; rebuild this release")
    launch_command = ([str(launcher)] if launcher else
                      ["/usr/bin/python3", str(root / "tools/manage.py"),
                       "--config", str(config_path), "launch"])
    command = ["bash", str(installer), "install", "--user", desktop_user(),
               "--directory", str(root), "--autologin", "yes" if mode == "enabled" else "no",
               "--", *launch_command]
    if os.geteuid() != 0:
        command.insert(0, "sudo")
    subprocess.run(command, check=True)


def prepare_system_setup(root, *, first_install, mode=None, setup_system=False):
    """Persist pending provisioning before activation, allowing failed setup retries."""
    path = root / "update-state/system-setup.json"
    state = json.loads(path.read_text()) if path.exists() else None
    if setup_system or (first_install and (state is None or state["complete"])):
        state = {"complete": False, "kiosk": mode or "enabled"}
        atomic_json(path, state)
    elif first_install and mode is not None:
        state = {"complete": False, "kiosk": mode}
        atomic_json(path, state)
    elif mode is not None and not (state is not None and not state["complete"] and state["kiosk"] == mode):
        raise ValueError("Use --setup-system to change kiosk on an existing installation")
    return state


def finish_system_setup(root, config_path, state, launcher=None):
    if state is None or state["complete"]:
        from src.engine.updates.remote_support import reconcile, release_settings
        release = root / 'current'
        if release_settings(release) is not None:
            helper = release / 'platform/installation/remote-support/install_update_helper.sh'
            command = ['bash', str(helper), desktop_user()]
            if os.geteuid() != 0:
                command.insert(0, 'sudo')
            subprocess.run(command, check=True)
            reconcile(release)
        print("Software installation only; existing system and kiosk settings preserved.")
        return
    try:
        install_remote_support(root)
        install_kiosk(root, config_path, state["kiosk"], launcher=launcher)
    except (OSError, subprocess.SubprocessError, RuntimeError) as error:
        raise RuntimeError("Platform software installed, but system setup is incomplete; "
                           "rerun the installer to retry: " + str(error)) from error
    atomic_json(root / "update-state/system-setup.json", {**state, "complete": True})
    print("Initial system setup completed. Reboot when ready; no session was stopped.")


def install(args):
    with tarfile.open(args.archive.resolve(), "r:gz") as archive:
        member = archive.getmember("manifest.json")
        if member.size > 1024 * 1024 or not member.isfile():
            raise ValueError("Invalid local release manifest")
        local_manifest = json.load(archive.extractfile(member))
    product = local_manifest["product"]
    validate_manifest(local_manifest, product)
    initial_source = {}
    if local_manifest.get("format") == 2:
        with tarfile.open(args.archive.resolve(), "r:gz") as archive:
            seed_name = f"platform/_internal/config/update-source/{local_manifest['robot_system']}.json"
            try:
                seed = archive.getmember(seed_name)
            except KeyError:
                seed = None
            if seed is not None:
                if not seed.isfile() or seed.size > 1024 * 1024:
                    raise ValueError("Invalid bundled update-source configuration")
                initial_source = json.load(archive.extractfile(seed))
                if initial_source.get("product") != product:
                    raise ValueError("Bundled update source belongs to another robot system/profile")
    config_path = (args.config or default_config_path(product)).expanduser().resolve()
    if config_path.exists():
        config = UpdateConfig.load(config_path)
        root = (args.root.expanduser().resolve() if args.root else config.install_root)
        if config.install_root != root or config.product != product:
            raise ValueError("Existing configuration belongs to another robot system/profile installation")
    else:
        root = (args.root or default_install_root(product)).expanduser().resolve()
        atomic_json(config_path, {
            "enabled": False, "repository_url": "", "public_key": None,
            "channel": "stable", **initial_source,
            "product": product, "install_root": str(root),
        })
        config = UpdateConfig.load(config_path)
    updater = PlatformUpdater(config)
    with updater.offline():
        updater._recover()
        first_install = updater.installed() is None
        if args.storage_from:
            if updater.installed() or (updater.data.exists() and any(updater.data.iterdir())):
                raise ValueError("Storage import is allowed only into an empty first installation")
            source = args.storage_from.expanduser().resolve()
            profile = local_manifest.get("profile", "default")
            if (local_manifest.get("storage_system") == local_manifest.get("robot_system")
                    and profile != "default" and (source / "profiles" / profile / "storage").is_dir()):
                source = source / "profiles" / profile
            if not (source / "storage").is_dir():
                raise ValueError("--storage-from must be the old robot-system package directory containing storage/")
            if any(p.is_symlink() for p in source.rglob("*") if p.is_relative_to(source / "storage") or p.is_relative_to(source / "profiles")):
                raise ValueError("Resolve storage symlinks before import")
            temporary = root / ".storage-import"
            if temporary.exists():
                raise ValueError("Interrupted storage import found; inspect .storage-import before retrying")
            temporary.mkdir(parents=True)
            for name in ("storage", "profiles"):
                if (source / name).is_dir():
                    shutil.copytree(source / name, temporary / local_manifest.get("storage_system", "paint") / name)
            if updater.data.exists():
                updater.data.rmdir()
            os.rename(temporary, updater.data)
        system_setup = prepare_system_setup(
            root, first_install=first_install, mode=args.kiosk, setup_system=args.setup_system,
        )
    # Update the independent helper during a trusted installer maintenance run.
    # Subsequent refreshes atomically replace a symlink to a complete tool tree.
    tools = root / "tools"
    with updater.offline():
        tool_versions = root / "updater-tools"
        tool_versions.mkdir(exist_ok=True)
        new_tools = tool_versions / uuid.uuid4().hex
        new_tools.mkdir()
        shutil.copy2(__file__, new_tools / "manage.py")
        updater_source = Path(sys.modules[PlatformUpdater.__module__].__file__).parent
        shutil.copytree(updater_source, new_tools / "src/engine/updates", ignore=shutil.ignore_patterns("__pycache__"))
        (new_tools / "src/__init__.py").touch()
        (new_tools / "src/engine/__init__.py").touch()
        atomic_json(new_tools / "installation.json", {"product": product, "config_path": str(config_path)})
        sync_tree(new_tools)
        sync_directory(tool_versions)
        if tools.exists() and not tools.is_symlink():
            os.rename(tools, tool_versions / ("legacy-" + uuid.uuid4().hex))
        pointer = root / ".tools-new"
        pointer.unlink(missing_ok=True)
        pointer.symlink_to(new_tools.relative_to(root))
        os.replace(pointer, tools)
        sync_directory(root)
    current = updater.installed()
    if current != local_manifest:
        updater.stage_local(args.archive.resolve())
        updater.queue()
        updater.apply_pending()
    with updater.offline():
        finish_system_setup(root, config_path, system_setup)
    install_service(root, config_path)
    print(f"Installed platform at {root}\nUpdate configuration: {config_path}")
    print(f"Launch: /usr/bin/python3 '{tools / 'manage.py'}' --config '{config_path}' launch")


def launch(updater, config_path):
    def apply_or_reopen():
        if (updater.root / 'update-state/service.json').is_file():
            import time
            from src.engine.updates.service import request
            pending = updater.state / 'pending.json'
            journal = updater.state / 'transaction.json'
            requested = pending.exists() or journal.exists()
            deadline = time.monotonic() + 180
            while pending.exists() or journal.exists():
                if time.monotonic() >= deadline:
                    raise RuntimeError('Update service did not finish activation; inspect its journal')
                request(config_path, 'status', timeout=120)
                time.sleep(0.5)
            return requested
        try:
            return updater.apply_pending()
        except Exception as exc:
            if updater.installed() is None:
                raise
            print(f"Update failed; reopening the previous platform: {exc}", file=sys.stderr)
            return True

    if not (updater.root / 'update-state/service.json').is_file():
        updater.recover()
    apply_or_reopen()
    while True:
        helper = updater.root / "tools/manage.py"
        if (HERE.is_relative_to(updater.root / "updater-tools")
                and helper.is_file() and helper.resolve() != Path(__file__).resolve()):
            # Release the update locks before loading the newly activated helper.
            os.execv("/usr/bin/python3", ["/usr/bin/python3", str(helper),
                                       "--config", str(config_path.resolve()), "launch"])
        with lock(updater.root / 'runtime.lock', shared=True), lock(updater.state / "runtime.lock", shared=True):
            current = updater.installed()
            if current is None:
                raise ValueError("Platform is not installed")
            combined = current.get('component') == 'robot'
            executable = (updater.root / 'current/launch.sh' if combined else
                          updater.root / "current/platform" / release_executable(current))
            env = dict(os.environ)
            env["ROBOT_PLATFORM_DATA_ROOT"] = str(updater.data)
            env["ROBOT_PLATFORM_PRODUCT"] = current["product"]
            env["ROBOT_PLATFORM_UPDATE_CONFIG"] = str(config_path.resolve())
            for key in ("VIRTUAL_ENV", "PYTHONHOME", "PYTHONPATH"):
                env.pop(key, None)
            result = subprocess.run([str(executable)], cwd=executable.parent, env=env)
        if result.returncode != 0:
            print("Platform exited with an error; pending update remains unapplied", file=sys.stderr)
            return result.returncode
        if combined and not (updater.root / 'update-state/service.json').is_file() and (updater.state / 'pending.json').exists():
            # Do not switch the pair while a backend from the old release is running.
            subprocess.run([str(updater.root / 'current/backend/stop.sh')],
                           env=subprocess_environment(), check=True, timeout=60)
        applied = apply_or_reopen()
        changed = updater.installed()['version'] != current['version']
        if not applied and not changed:
            return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path)
    commands = parser.add_subparsers(dest="command", required=True)
    installer = commands.add_parser("install")
    installer.add_argument("archive", type=Path)
    installer.add_argument("--config", type=Path, default=argparse.SUPPRESS)
    installer.add_argument("--root", type=Path)
    installer.add_argument("--storage-from", type=Path)
    installer.add_argument("--kiosk", choices=("enabled", "manual", "off"),
                           help="First install: enabled (default), manual login, or skip kiosk")
    installer.add_argument("--setup-system", action="store_true",
                           help="Explicitly rerun SSH, RustDesk and kiosk setup on an existing install")
    # Shared provisioning entry point used by the combined robot installer.
    setup = commands.add_parser("setup-system")
    setup.add_argument("--root", type=Path, required=True)
    setup.add_argument("--launcher", type=Path, required=True)
    setup.add_argument("--first-install", action="store_true")
    setup.add_argument("--setup-system", action="store_true")
    setup.add_argument("--kiosk", choices=("enabled", "manual", "off"))
    for name in ("check", "stage", "queue", "apply", "launch", "recover", "serve", "install-service"):
        commands.add_parser(name)
    rollback = commands.add_parser("rollback")
    rollback.add_argument("--restore-pre-update-data", action="store_true", required=True,
                          help="Restore the data snapshot; newer data stays in an additional backup")
    args = parser.parse_args()
    try:
        if args.command == "setup-system":
            root = args.root.expanduser().resolve()
            with lock(root / "runtime.lock"):
                state = prepare_system_setup(root, first_install=args.first_install,
                                             mode=args.kiosk, setup_system=args.setup_system)
                finish_system_setup(root, None, state, launcher=args.launcher.expanduser().absolute())
            return 0
        if args.command == "install":
            install(args)
            return 0
        if args.config is None:
            metadata = HERE / "installation.json"
            args.config = (Path(json.loads(metadata.read_text())["config_path"])
                           if metadata.is_file() else default_config_path())
        if args.command == 'serve':
            from src.engine.updates.service import serve
            serve(args.config)
            return 0
        if args.command == 'install-service':
            from src.engine.updates.service_install import install_service
            config = UpdateConfig.load(args.config)
            install_service(config.install_root, args.config)
            return 0
        updater = PlatformUpdater(UpdateConfig.load(args.config))
        if args.command == "launch":
            return launch(updater, args.config)
        if args.command in {"check", "stage"}:
            result = updater.check() if args.command == "check" else updater.stage_latest()
            print(json.dumps(result, indent=2))
        elif args.command == "queue":
            updater.queue()
        elif args.command == "apply":
            updater.apply_pending()
        elif args.command == "recover":
            updater.recover()
        elif args.command == "rollback":
            updater.rollback()
        return 0
    except Exception as exc:
        print(f"Platform operation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
