"""Declarative build identities; importing this module never constructs hardware."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "config/release_targets.json"


def application_asset_data(target: dict, root: Path = ROOT) -> list[tuple[str, str]]:
    """Collect application-owned assets only from the selected system packages."""
    data = []
    for package in target["packages"]:
        applications = root / "src/robot_systems" / package / "applications"
        for assets in sorted(applications.glob("*/assets")):
            if assets.is_dir():
                data.append((str(assets), str(assets.relative_to(root))))
    return data


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
    (destination / "backend_network.json").write_text(
        (ROOT / "config/backend_network.json").read_text(encoding="utf-8"), encoding="utf-8"
    )
    (destination / "platform.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (destination / "release-target.json").write_text(json.dumps(target, indent=2), encoding="utf-8")
    factory = ROOT / "config/factory_defaults" / f"{name}.json"
    (destination / "factory-defaults.json").write_text(factory.read_text(encoding="utf-8"), encoding="utf-8")
    update_source = load_update_source(target)
    source_dir = destination / 'update-source'
    source_dir.mkdir(exist_ok=True)
    (source_dir / f'{name}.json').write_text(json.dumps(update_source, indent=2), encoding='utf-8')
    return target


def load_update_source(target: dict) -> dict:
    """Package the selected system's declaration, never a repository built into engine."""
    source = target.get('update_source')
    if source is None:
        return {'enabled': False, 'product': target['product'], 'repository_url': '', 'public_key': None}
    if not isinstance(source, str) or not source:
        raise ValueError('update_source must name a system-owned JSON file')
    path = (ROOT / source).resolve()
    system_root = (ROOT / 'src/robot_systems' / target['robot_system']).resolve()
    if not path.is_relative_to(system_root):
        raise ValueError('update_source must remain inside the selected robot system package')
    payload = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(payload, dict) or payload.get('product') != target['product']:
        raise ValueError('Update source belongs to another robot system/product')
    if not isinstance(payload.get('enabled', False), bool):
        raise ValueError('Update source enabled must be a boolean')
    return payload
