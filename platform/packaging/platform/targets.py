"""Declarative build identities; importing this module never constructs hardware."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "config/release_targets.json"


def load_target(name: str) -> dict:
    targets = json.loads(CATALOG.read_text(encoding="utf-8"))
    if name not in targets:
        raise ValueError(f"Unknown release target {name!r}; choose: {', '.join(targets)}")
    target = dict(targets[name], target=name)
    target["executable"] = target["product"]
    return target


def prepare_target(name: str, destination: Path) -> dict:
    target = load_target(name)
    destination.mkdir(parents=True, exist_ok=True)
    # Runtime and component packaging share the selected system configuration.
    import sys
    sys.path.insert(0, str(ROOT))
    from src.bootstrap.startup_config import load_robot_system_config
    payload = json.loads((ROOT / "config/platform.json").read_text())
    selected = load_robot_system_config(payload, name)
    payload.update(robot_system=name, supported_robot_systems=[name], robot_systems={name: selected})
    payload["ros_backend"] = {**payload.get("ros_backend", {}), "auto_launch": True, "auto_stop": True}
    payload["ros_backend"].pop("launch_script", None)
    payload["ros_backend"].pop("stop_script", None)
    (destination / "platform.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (destination / "release-target.json").write_text(json.dumps(target, indent=2), encoding="utf-8")
    factory = ROOT / "config/factory_defaults" / f"{name}.json"
    (destination / "factory-defaults.json").write_text(factory.read_text(encoding="utf-8"), encoding="utf-8")
    return target
