import importlib.util
import io
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tarfile
import tempfile
import unittest
from unittest.mock import patch

from src.engine.updates.config import UpdateConfig, default_config_path, default_install_root
from src.engine.updates.updater import PlatformUpdater

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("platform_release_targets", ROOT / "packaging/platform/targets.py")
targets = importlib.util.module_from_spec(spec)
spec.loader.exec_module(targets)


class ReleaseTargetTests(unittest.TestCase):
    def test_release_config_disables_development_login_bypass(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            targets.prepare_target("paint_tray_dry", destination)
            configuration = json.loads((destination / "platform.json").read_text())
            self.assertIs(configuration["ui"]["dev_skip_login"], False)

    def test_update_source_can_be_omitted_for_system_without_remote_updates(self):
        source = targets.load_update_source({'product': 'custom-robot'})
        self.assertFalse(source['enabled'])

    def test_system_owned_sources_are_independent_and_cannot_cross_packages(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(targets, 'ROOT', Path(folder)):
            for name in ('first', 'second'):
                path = Path(folder) / 'src/robot_systems' / name / 'storage/update_source.json'
                path.parent.mkdir(parents=True)
                path.write_text(json.dumps({'product': name, 'repository_url': f'https://github.com/owner/{name}',
                                            'repository_type': 'github', 'enabled': False}))
                target = {'product': name, 'robot_system': name, 'update_source': str(path.relative_to(folder))}
                self.assertEqual(targets.load_update_source(target)['repository_url'], f'https://github.com/owner/{name}')
                target['robot_system'] = 'other'
                with self.assertRaisesRegex(ValueError, 'selected robot system'):
                    targets.load_update_source(target)

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        os_patch = patch("platform.freedesktop_os_release", return_value={"ID": "ubuntu", "VERSION_ID": "24.04"})
        os_patch.start()
        self.addCleanup(os_patch.stop)

    def archive(self, target_name, version="1.0.0", *, override=None, factory=None):
        target = targets.load_target(target_name)
        manifest = {"format": 2, "product": target["product"], "version": version,
                    "architecture": platform.machine(), "os": "ubuntu-24.04", "storage_schema": 1,
                    **{k: target[k] for k in ("robot_system", "profile", "storage_system", "executable")}}
        manifest.update(override or {})
        marker = dict(target, **{k: manifest[k] for k in ("robot_system", "profile", "storage_system", "executable")})
        startup = {"robot_system": manifest["robot_system"], "supported_robot_systems": [manifest["robot_system"]]}
        seed = {"product": target["product"], "enabled": False,
                "repository_url": f"https://{target_name}.example/releases/", "public_key": None}
        files = {"platform/installation/remote-support/install.sh": b"#!/bin/sh\nexit 0\n",
                 "platform/installation/remote-support/install_pl_remote_support.sh": b"#!/bin/sh\nexit 0\n",
                 "manifest.json": json.dumps(manifest).encode(),
                 f"platform/{target['executable']}": b"#!/bin/sh\nexit 0\n",
                 "platform/_internal/config/release-target.json": json.dumps(marker).encode(),
                 "platform/_internal/config/platform.json": json.dumps(startup).encode(),
                 f"platform/_internal/config/update-source/{manifest['robot_system']}.json": json.dumps(seed).encode()}
        if factory is not None:
            files["platform/_internal/config/factory-defaults.json"] = json.dumps(factory).encode()
        archive = self.directory / f"{target_name}-{version}.tar.gz"
        with tarfile.open(archive, "w:gz") as bundle:
            for name, content in files.items():
                member = tarfile.TarInfo(name)
                member.size = len(content)
                member.mode = 0o755 if name == f"platform/{target['executable']}" else 0o644
                bundle.addfile(member, io.BytesIO(content))
        return archive

    def test_each_target_has_a_unique_product_and_valid_bootstrap_provider(self):
        from src.bootstrap.startup_config import load_startup_config, load_bootstrap_provider
        products = set()
        for name in json.loads(targets.CATALOG.read_text()):
            with self.subTest(target=name):
                source_config = json.loads((ROOT / "config/platform.json").read_text())
                selected = dict(robot_driver="zeroerr", backend="zeroerr", backend_profile="paint_short_links",
                                release_version="1.0.0", platform_version="1.0.0", backend_version="1.0.0")
                source_config["robot_systems"] = {name: selected}
                original_read = Path.read_text
                def read_config(path, *args, **kwargs):
                    if path == ROOT / "config/platform.json":
                        return json.dumps(source_config)
                    return original_read(path, *args, **kwargs)
                with patch.object(Path, "read_text", read_config):
                    target = targets.prepare_target(name, self.directory / name)
                self.assertNotIn(target["product"], products)
                products.add(target["product"])
                self.assertEqual((self.directory / name / "backend_network.json").read_text(),
                                 (ROOT / "config/backend_network.json").read_text())
                config = load_startup_config(self.directory / name / "platform.json")
                seed = json.loads((self.directory / name / 'update-source' / f'{name}.json').read_text())
                self.assertEqual(seed['product'], target['product'])
                self.assertEqual(seed, json.loads((ROOT / target['update_source']).read_text()))
                provider = load_bootstrap_provider(config)
                self.assertEqual((name,), config.supported_robot_systems)
                self.assertIn(provider.system_class.__module__.split(".")[2], target["packages"])

    def test_dedicated_configuration_and_installation_paths_do_not_collide(self):
        catalog = json.loads(targets.CATALOG.read_text())
        with patch("pathlib.Path.home", return_value=self.directory), patch.dict(os.environ, {}, clear=True):
            paths = [default_config_path(item["product"]) for item in catalog.values()]
            roots = [default_install_root(item["product"]) for item in catalog.values()]
        self.assertEqual(len(catalog), len(set(paths)))
        self.assertEqual(len(catalog), len(set(roots)))
        self.assertTrue(all(path.name == "updates.json" for path in paths))

    def test_each_target_has_its_own_matching_source_configuration(self):
        for name, target in json.loads(targets.CATALOG.read_text()).items():
            with self.subTest(target=name):
                source = targets.load_update_source(targets.load_target(name))
                self.assertEqual(target["product"], source["product"])
                if name == "paint_tray_dry":
                    self.assertTrue(source["enabled"])
                    self.assertEqual(source["repository_type"], "github")
                    self.assertEqual(source["repository_url"],
                                     "https://github.com/VentsiIliev/robot_platform_backend_svn_mirror")
                    self.assertTrue(source["allow_insecure_http"])
                else:
                    self.assertFalse(source["enabled"])

    def test_shared_editor_can_load_without_the_paint_package(self):
        script = (
            "import sys; sys.modules['src.robot_systems.paint'] = None; "
            "from src.applications.workpiece_editor.editor_core.config import SegmentEditorConfig"
        )
        subprocess.run([str(ROOT / ".venv/bin/python"), "-c", script],
                       cwd=ROOT, check=True, capture_output=True)

    def test_legacy_paint_paths_are_preserved_when_already_installed(self):
        legacy_config = self.directory / ".config/robot-platform/updates.json"
        legacy_config.parent.mkdir(parents=True)
        legacy_config.write_text("{}")
        legacy_data = self.directory / ".local/share/robot-platform/data"
        legacy_data.mkdir(parents=True)
        with patch("pathlib.Path.home", return_value=self.directory), patch.dict(os.environ, {}, clear=True):
            self.assertEqual(legacy_config, default_config_path("paint-robot"))
            self.assertEqual(legacy_data.parent, default_install_root("paint-robot"))
            self.assertNotEqual(legacy_config, default_config_path("paint-tray-dry-robot"))

    def test_tray_install_rejects_an_automatic_dryer_release(self):
        root = self.directory / "tray"
        updater = PlatformUpdater(UpdateConfig(root, "", None, product="paint-tray-dry-robot"))
        updater.stage_local(self.archive("paint_tray_dry"))
        updater.queue()
        updater.apply_pending()
        with self.assertRaises(ValueError):
            updater.stage_local(self.archive("paint_auto_dry", "1.1.0"))
        self.assertEqual("tray_dryer", updater.installed()["profile"])
        with self.assertRaises(ValueError):
            PlatformUpdater(UpdateConfig(root, "https://other.example/", None, product="paint-auto-dry-robot"))

    def test_same_product_with_wrong_profile_is_rejected(self):
        updater = PlatformUpdater(UpdateConfig(self.directory / "tray", "", None, product="paint-tray-dry-robot"))
        updater.stage_local(self.archive("paint_tray_dry"))
        updater.queue()
        updater.apply_pending()
        with self.assertRaisesRegex(ValueError, "another robot system/profile"):
            updater.stage_local(self.archive("paint_tray_dry", "1.1.0", override={"profile": "automatic_dryer"}))

    def test_separate_products_can_use_the_same_version_and_different_repositories(self):
        for name in ("paint_tray_dry", "paint_auto_dry", "glue", "twin_robot"):
            target = targets.load_target(name)
            updater = PlatformUpdater(UpdateConfig(self.directory / name, f"https://{name}.example/", None, product=target["product"]))
            updater.stage_local(self.archive(name))
            updater.queue()
            updater.apply_pending()
            self.assertEqual("1.0.0", updater.installed()["version"])
            self.assertEqual(target["product"], updater.installed()["product"])

    def test_installer_creates_each_products_source_file_and_preserves_it(self):
        manager = ROOT / "packaging/runtime/manage.py"
        environment = dict(os.environ, PYTHONPATH="")
        # This test covers product config persistence, not host provisioning.
        # Keep the actual installer CLI and mock only privileged setup steps.
        bootstrap = """
import importlib.util
import sys
from unittest.mock import patch
sys.argv = sys.argv[1:]
spec = importlib.util.spec_from_file_location('platform_manager', sys.argv[0])
manager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manager)
with patch.object(manager, 'install_remote_support'), patch.object(manager, 'install_kiosk'), patch.object(manager, 'install_service'):
    sys.exit(manager.main())
"""
        for name in ("paint_tray_dry", "paint_auto_dry", "glue", "twin_robot"):
            config = self.directory / name / "updates.json"
            root = self.directory / name / "installed"
            archive = self.archive(name)
            args = ["/usr/bin/python3", "-c", bootstrap, str(manager), "--config", str(config), "install", str(archive), "--root", str(root)]
            subprocess.run(args, check=True, capture_output=True, env=environment, cwd="/tmp")
            raw = json.loads(config.read_text())
            self.assertEqual(f"https://{name}.example/releases/", raw["repository_url"])
            raw["repository_url"] = f"https://custom-{name}.example/"
            config.write_text(json.dumps(raw))
            before = config.read_bytes()
            subprocess.run(args, check=True, capture_output=True, env=environment, cwd="/tmp")
            self.assertEqual(before, config.read_bytes())
            # Installed helpers find their own dedicated file without --config.
            subprocess.run(["/usr/bin/python3", str(root / "tools/manage.py"), "recover"], check=True, capture_output=True, env=environment, cwd="/tmp")

    def test_release_builder_rejects_a_bundle_for_another_profile(self):
        bundle = self.directory / "wrong-bundle"
        marker = bundle / "_internal/config/release-target.json"
        marker.parent.mkdir(parents=True)
        marker.write_text(json.dumps(targets.load_target("paint_tray_dry")))
        (bundle / "paint-auto-dry-robot").write_text("wrong profile")
        result = subprocess.run(["/usr/bin/python3", str(ROOT / "packaging/platform/build_release.py"), "paint_auto_dry", "1.0.0", "--bundle", str(bundle), "--output", str(self.directory / "output")], capture_output=True, text=True)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("Bundle identity does not match", result.stderr)
        self.assertFalse((self.directory / "output").exists())

    def test_release_archive_carries_runnable_updater_sources(self):
        target = targets.load_target("paint_tray_dry")
        bundle = self.directory / "bundle"
        config = bundle / "_internal/config"
        config.mkdir(parents=True)
        (bundle / target["executable"]).write_text("#!/bin/sh\nexit 0\n")
        (config / "release-target.json").write_text(json.dumps(target))
        (config / "factory-defaults.json").write_bytes((ROOT / "config/factory_defaults/paint_tray_dry.json").read_bytes())
        updater = bundle / "installation/updater"
        (updater / "src/engine").mkdir(parents=True)
        shutil.copy2(ROOT / "packaging/runtime/manage.py", updater / "manage.py")
        shutil.copytree(
            ROOT / "src/engine/updates", updater / "src/engine/updates",
            ignore=shutil.ignore_patterns("__pycache__"),
        )
        shutil.copy2(ROOT / "src/__init__.py", updater / "src/__init__.py")
        shutil.copy2(ROOT / "src/engine/__init__.py", updater / "src/engine/__init__.py")
        output = self.directory / "output"
        subprocess.run(["/usr/bin/python3", str(ROOT / "packaging/platform/build_release.py"),
                        "paint_tray_dry", "1.0.0", "--bundle", str(bundle), "--output", str(output)],
                       check=True, capture_output=True)
        archive = next((output / "paint_tray_dry/stable").glob("*.tar.gz"))
        with tarfile.open(archive) as release:
            names = release.getnames()
            prefix = "platform/installation/updater"
            self.assertIn(prefix + "/manage.py", names)
            self.assertIn(prefix + "/src/engine/updates/updater.py", names)
            self.assertIn("platform/installation/account-maintenance/account-maintenance.pyz", names)
            self.assertIn("platform/installation/account-maintenance/install.py", names)
            self.assertEqual(len(names), len(set(names)), "release archive has duplicate entries")
            self.assertFalse(any("__pycache__" in name for name in names))
        # Verify independent imports under system Python.
        extracted = self.directory / "extracted"
        with tarfile.open(archive) as release:
            for member in release:
                if member.name.startswith(prefix + "/") and member.isfile():
                    destination = extracted / member.name
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(release.extractfile(member).read())
        subprocess.run(["/usr/bin/python3", str(extracted / prefix / "manage.py"), "--help"],
                       cwd="/tmp", check=True, capture_output=True)

    def test_activation_preserves_explicitly_provisioned_factory_settings(self):
        factory = json.loads((ROOT / "config/factory_defaults/paint_tray_dry.json").read_text())
        updater = PlatformUpdater(UpdateConfig(self.directory / "tray", "", None, product="paint-tray-dry-robot"))
        settings = updater.data / "paint_tray_dry/storage/settings"
        saved = settings / "hardware/modbus.json"
        saved.parent.mkdir(parents=True)
        saved.write_text('{"port": "operator-port", "baudrate": 9600}')
        before = saved.read_bytes()
        # Existing installations provision new settings explicitly before upgrade.
        for relative, value in factory['files'].items():
            destination = settings / relative
            if not destination.exists():
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(json.dumps(value))
        updater.stage_local(self.archive("paint_tray_dry", factory=factory))
        updater.queue()
        updater.apply_pending()
        self.assertEqual(before, saved.read_bytes())
        devices = settings / "hardware/peripherals.json"
        self.assertIn("tray_fan", json.loads(devices.read_text()))
        devices.write_text('{"operator_device": {"enabled": false}}')
        before_devices = devices.read_bytes()
        updater.stage_local(self.archive("paint_tray_dry", "1.1.0", factory=factory))
        updater.queue()
        updater.apply_pending()
        self.assertEqual(before, saved.read_bytes())
        self.assertEqual(before_devices, devices.read_bytes())

    def test_activation_moves_legacy_profile_storage_and_rollback_restores_it(self):
        updater = PlatformUpdater(UpdateConfig(self.directory / 'legacy-tray', '', None,
                                               product='paint-tray-dry-robot'))
        legacy = updater.data / 'paint/profiles/tray_dryer/storage/users/users.csv'
        legacy.parent.mkdir(parents=True)
        legacy.write_text('existing accounts')
        updater.stage_local(self.archive('paint_tray_dry', override={'storage_system': 'paint'}))
        updater.queue()
        updater.apply_pending()
        updater.stage_local(self.archive('paint_tray_dry', '1.1.0'))
        updater.queue()
        updater.apply_pending()
        destination = updater.data / 'paint_tray_dry/storage/users/users.csv'
        self.assertEqual('existing accounts', destination.read_text())
        self.assertFalse(legacy.exists())
        updater.rollback()
        self.assertEqual('existing accounts', legacy.read_text())
        self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()
