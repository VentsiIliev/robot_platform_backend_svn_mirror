import ast
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGING_ROOT = ROOT / "packaging/platform"


class TestPaintPackagingProfile(unittest.TestCase):
    def test_bundled_startup_config_selects_only_paint(self):
        config = json.loads(
            (PACKAGING_ROOT / "paint_config" / "platform.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(config["robot_system"], "paint")
        self.assertEqual(config["supported_robot_systems"], ["paint"])

    def test_spec_excludes_other_robot_systems(self):
        targets = json.loads((ROOT / "config/release_targets.json").read_text())
        tree = ast.parse((PACKAGING_ROOT / "platform.spec").read_text())
        expression = next(node.value for node in tree.body
                          if isinstance(node, ast.Assign)
                          and any(isinstance(name, ast.Name) and name.id == "excluded"
                                  for name in node.targets))
        excluded = eval(compile(ast.Expression(expression), "platform.spec", "eval"),
                        {"ROOT": ROOT, "target": targets["paint"]})
        for package in ("glue", "welding", "paint_auto_dry", "paint_tray_dry", "ROBOT_SYSTEM_BLUEPRINT"):
            self.assertIn(f"src.robot_systems.{package}", excluded)
        self.assertNotIn("src.robot_systems.paint", excluded)

    def test_build_script_checks_collected_module_archive(self):
        wrapper = (PACKAGING_ROOT / "build.sh").read_text(encoding="utf-8")
        self.assertIn('packaging/platform/build.py', wrapper)
        script = (PACKAGING_ROOT / "build.py").read_text(encoding="utf-8")
        self.assertIn("PYZ-00.toc", script)
        self.assertIn('allowed = set(target["packages"])', script)
        self.assertIn("Other robot system bundled", script)


def _literal_assignments(path: Path) -> dict[str, object]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    assignments = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue
        try:
            assignments[target.id] = ast.literal_eval(node.value)
        except (ValueError, TypeError):
            continue
    return assignments


if __name__ == "__main__":
    unittest.main()
