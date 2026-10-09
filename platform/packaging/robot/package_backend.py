#!/usr/bin/env python3
"""Build and package a target-specific ROS runtime without launching hardware."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import tarfile
import tempfile
import sys

ROOT = Path(__file__).resolve().parents[3]
WORKSPACE = ROOT / "backend/ros2_ws"
sys.path.insert(0, str(ROOT / "platform"))
from src.bootstrap.startup_config import load_robot_system_config


def run(command, **kwargs):
    subprocess.run(command, check=True, **kwargs)


def verify(root):
    """Reject missing resources and links escaping the release."""
    for path in root.rglob("*"):
        if path.is_symlink():
            resolved = path.resolve(strict=True)
            if not resolved.is_relative_to(root.resolve()):
                raise ValueError(f"External runtime symlink: {path}")
    for resource in ("install/local_setup.bash", "install/share/zeroerr/scripts/EtherCatStart.sh",
                     "install/share/zeroerr/scripts/resolve_ethercat_nic.sh",
                     "install/share/zeroerr/config/runtime.yaml", "launch.sh", "stop.sh"):
        if not (root / resource).is_file():
            raise ValueError(f"Missing runtime resource: {resource}")
    for script in root.rglob("*.sh"):
        run(["bash", "-n", str(script)])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", choices=("paint_tray_dry",))
    parser.add_argument("--ros-distro", choices=("jazzy",), default="jazzy")
    parser.add_argument("--output", type=Path, default=ROOT / "releases")
    parser.add_argument("--verify-only", action="store_true", help="Build and verify uncommitted changes without creating a release")
    args = parser.parse_args()
    try:
        payload = json.loads((ROOT / "platform/config/platform.json").read_text())
        selected = load_robot_system_config(payload, args.target)
    except (RuntimeError, ValueError) as exc:
        parser.error(str(exc))
    version = selected["backend_version"]
    target = {"backend": selected["backend"], "profile": selected["backend_profile"]}
    if target["backend"] != "zeroerr":
        parser.error("Only ZeroErr packaging is implemented")
    os_release = Path("/etc/os-release").read_text()
    if 'VERSION_ID="24.04"' not in os_release or 'ID=ubuntu' not in os_release:
        parser.error("Build on Ubuntu 24.04")
    setup = Path("/opt/ros") / args.ros_distro / "setup.bash"
    if not setup.is_file():
        parser.error(f"Missing ROS installation: {setup}")
    output = args.output.resolve() / args.target / "backend" / version
    if output.exists() and not args.verify_only:
        parser.error(f"Release output already exists: {output}")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    message = subprocess.check_output(["git", "log", "-1", "--format=%B"], cwd=ROOT, text=True)
    revision = re.search(r"git-svn-id: .*@(\d+) ", message)
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip())
    if dirty and not args.verify_only:
        parser.error("Commit source changes before producing a release; working tree is dirty")
    with tempfile.TemporaryDirectory(prefix="robot-backend-build-") as directory:
        work = Path(directory)
        bundle = work / "backend"
        bundle.mkdir()
        env = dict(os.environ)
        for key in ("AMENT_PREFIX_PATH", "COLCON_PREFIX_PATH", "CMAKE_PREFIX_PATH", "ROS_PACKAGE_PATH",
                    "PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV", "ROS_DISTRO", "ROS_VERSION", "ROS_PYTHON_VERSION"):
            env.pop(key, None)
        env["PATH"] = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
        run(["bash", "-c", 'source "$1"; exec colcon --log-base "$2" build --base-paths "$3/src" "$3/eRob_moveit/src" --build-base "$4" --install-base "$5" --merge-install --packages-up-to erob_moveit_runtime zeroerr --cmake-args -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF -DPython3_EXECUTABLE=/usr/bin/python3',
             "backend-release", str(setup), str(work / "log"), str(WORKSPACE), str(work / "build"), str(bundle / "install")], cwd=work, env=env)
        launch_dir = bundle / "eRob_moveit"
        launch_dir.mkdir()
        for name in ("launch_robot.sh", "zeroerr_rt_policy.env"):
            shutil.copy2(WORKSPACE / "eRob_moveit" / name, launch_dir / name)
        config = (WORKSPACE / "eRob_moveit/zeroerr_launch.conf").read_text()
        config = config.replace('${SCRIPT_DIR}/src/eRob_ROS2_MoveIt/zeroerr/scripts/EtherCatStart.sh', '${ROOT_WS_DIR}/install/share/zeroerr/scripts/EtherCatStart.sh')
        config = config.replace('${ROS_SETUP_FILE:-${DEFAULT_ROS_SETUP_FILE}}', '/opt/ros/jazzy/setup.bash')
        config += '\nexport ROBOT_RELEASE_TARGET=' + args.target + '\nexport ZEROERR_ACTIVE_PROFILE=' + target["profile"] + '\n'
        (launch_dir / "zeroerr_launch.conf").write_text(config)
        # This helper is used by EtherCatStart.sh but is absent from its CMake install list.
        shutil.copy2(WORKSPACE / "eRob_moveit/src/eRob_ROS2_MoveIt/zeroerr/scripts/resolve_ethercat_nic.sh", bundle / "install/share/zeroerr/scripts/resolve_ethercat_nic.sh")
        for action in ("launch", "stop"):
            script = bundle / (action + ".sh")
            script.write_text('#!/usr/bin/env bash\nset -euo pipefail\nROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"\nexport ROS_SETUP_FILE=/opt/ros/jazzy/setup.bash\nexport ROBOT_LAUNCH_CONFIG="$ROOT/eRob_moveit/zeroerr_launch.conf"\nexport ROBOT_LAUNCH_ACTION=' + action + '\nexec "$ROOT/eRob_moveit/launch_robot.sh" "$@"\n')
            script.chmod(0o755)
        requirements = bundle / "requirements"
        requirements.mkdir()
        for name in ("requirements_apt.txt", "requirements_bridge.txt", "WORKSPACE_REQUIREMENTS.md"):
            shutil.copy2(WORKSPACE / name, requirements / name)
        manifest = {"format": 1, "component": "backend", "target": args.target, "version": version,
                    "backend": target["backend"], "profile": target["profile"], "os": "ubuntu-24.04",
                    "ros_distro": args.ros_distro, "architecture": platform.machine(), "source_git_commit": commit,
                    "source_svn_revision": revision.group(1) if revision else None}
        (bundle / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        verify(bundle)
        # Verify ROS package discovery after relocation; no nodes or hardware are started.
        relocated = work / "relocated/backend"
        shutil.copytree(bundle, relocated, symlinks=True)
        verify(relocated)
        run(["bash", "-c", 'source "$1"; source "$2/install/local_setup.bash"; for package in zeroerr erob_moveit_runtime ethercat_driver ethercat_generic_cia402_drive; do prefix=$(ros2 pkg prefix "$package") || exit; [[ "$prefix" == "$2/install" ]] || exit 1; done', "verify", str(setup), str(relocated)], cwd=work, env=env)
        if args.verify_only:
            print("Backend build and relocation verification passed; no release created")
            return
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=output.parent, prefix=".release-") as staging:
            staged = Path(staging)
            archive = staged / f"{args.target}-backend-{version}-{platform.machine()}.tar.gz"
            with tarfile.open(archive, "w:gz") as destination:
                destination.add(bundle, arcname="backend", filter=lambda member: None if "__pycache__" in Path(member.name).parts else member)
            with archive.open("rb") as stream:
                checksum = hashlib.file_digest(stream, "sha256").hexdigest()
            (staged / (archive.name + ".sha256")).write_text(f"{checksum}  {archive.name}\n")
            (staged / "manifest.json").write_text(json.dumps({**manifest, "archive": archive.name, "sha256": checksum}, indent=2) + "\n")
            staged.rename(output)
        print(output)


if __name__ == "__main__":
    main()
