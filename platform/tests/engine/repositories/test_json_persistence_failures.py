import json
import multiprocessing
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from src.engine.auth.json_permissions_repository import JsonPermissionsRepository
from src.engine.repositories.json.json_store import JsonStoreError
from src.engine.repositories.settings_service import SettingsService
from src.engine.repositories.settings_service_factory import build_from_specs
from src.engine.repositories.interfaces import SettingsLoadError
from src.shared_contracts.declarations import SettingsSpec
from tests.engine.repositories.test_settings_service_factory import SettingsIDTestEnum, _Ser, FakeSystem


def _write_permission(path, app):
    JsonPermissionsRepository(path).set_allowed_role_values(app, ['Admin'])


class TestPersistenceFailures(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / 'permissions.json'
        self.path.write_text('{}')

    def test_permissions_no_lost_updates_between_instances_and_processes(self):
        first = JsonPermissionsRepository(str(self.path))
        second = JsonPermissionsRepository(str(self.path))
        first.set_allowed_role_values('first', ['Admin'])
        second.set_allowed_role_values('second', ['Operator'])
        self.assertEqual(set(first.get_all()), {'first', 'second'})
        ctx = multiprocessing.get_context('fork')
        processes = [ctx.Process(target=_write_permission, args=(str(self.path), f'p{i}')) for i in range(4)]
        for process in processes:
            process.start()
        for process in processes:
            process.join(10)
            if process.is_alive():
                process.terminate()
                process.join()
                self.fail('Permission writer deadlocked')
            self.assertEqual(process.exitcode, 0)
        self.assertEqual(len(first.get_all()), 6)

    def test_permissions_failed_save_does_not_change_effective_roles(self):
        repo = JsonPermissionsRepository(str(self.path))
        repo.set_allowed_role_values('app', ['Admin'])
        with patch('src.engine.core.durable_files.os.replace', side_effect=OSError('failed')):
            with self.assertRaises(OSError):
                repo.set_allowed_role_values('app', ['Operator'])
        self.assertEqual(repo.get_allowed_role_values('app'), ['Admin'])

    def test_permissions_corruption_and_deletion_never_use_cached_roles(self):
        repo = JsonPermissionsRepository(str(self.path), ['Admin'])
        for content in ('', '{broken', '[]', '{"app":"Admin"}', '{"app":[1]}'):
            self.path.write_text(content)
            with self.assertRaises(JsonStoreError):
                repo.get_allowed_role_values('app')
            with self.assertRaises(JsonStoreError):
                repo.set_allowed_role_values('new', ['Admin'])
            self.assertEqual(self.path.read_text(), content)
        self.path.unlink()
        with self.assertRaises(JsonStoreError):
            repo.get_all()

    def test_settings_cache_isolated_and_evicted_on_failed_save_and_reload(self):
        repo = Mock()
        repo.load.return_value = {'value': 1}
        service = SettingsService({SettingsIDTestEnum.A: repo})
        candidate = service.get(SettingsIDTestEnum.A)
        candidate['value'] = 99
        self.assertEqual(service.get(SettingsIDTestEnum.A), {'value': 1})
        repo.save.side_effect = OSError('failed')
        with self.assertRaises(OSError):
            service.save(SettingsIDTestEnum.A, candidate)
        self.assertEqual(service.get(SettingsIDTestEnum.A), {'value': 1})
        repo.load.side_effect = SettingsLoadError('corrupt')
        with self.assertRaises(SettingsLoadError):
            service.reload(SettingsIDTestEnum.A)
        with self.assertRaises(SettingsLoadError):
            service.get(SettingsIDTestEnum.A)

    def test_required_setting_spec_enforced_and_optional_missing_explicit(self):
        service = build_from_specs([
            SettingsSpec(SettingsIDTestEnum.A, _Ser(), 'required.json'),
            SettingsSpec(SettingsIDTestEnum.B, _Ser(), 'optional.json', required=False),
        ], str(self.path.parent), FakeSystem)
        with self.assertRaises(SettingsLoadError):
            service.get(SettingsIDTestEnum.A)
        self.assertEqual(service.get(SettingsIDTestEnum.B).value, 'default')
        self.assertFalse(Path(service.get_repo(SettingsIDTestEnum.B).file_path).exists())

    def test_glue_update_failure_keeps_json_and_corrupt_reads_raise(self):
        from src.robot_systems.glue.domain.workpieces.repository.json_workpiece_repository import JsonWorkpieceRepository
        module = 'src.robot_systems.glue.domain.workpieces.repository.json_workpiece_repository'
        with patch(module + '.generate_thumbnail_bytes', return_value=None):
            repo = JsonWorkpieceRepository(str(self.path.parent / 'glue'))
            record = Path(repo.save({'name': 'old'}))
            before = record.read_bytes()
            with patch('src.engine.core.durable_files.os.replace', side_effect=OSError('failure')):
                with self.assertRaises(OSError):
                    repo.update(record.parent.name, {'name': 'new'})
            self.assertEqual(record.read_bytes(), before)
            record.write_text('{bad')
            with self.assertRaises(JsonStoreError):
                repo.load(record.parent.name)
            with self.assertRaises(JsonStoreError):
                repo.list_all()

    def test_choreography_corruption_is_not_an_empty_library(self):
        from src.robot_systems.twin_robot.storage.choreography_repository import ChoreographyRepository
        repo = ChoreographyRepository(str(self.path.parent / 'choreography'))
        (self.path.parent / 'choreography/broken.json').write_text('{bad')
        with self.assertRaises(JsonStoreError):
            repo.list()

    def test_paint_post_publication_sync_failure_blocks_record(self):
        from src.robot_systems.paint.domain.workpieces.repository.json_paint_workpiece_repository import (
            JsonPaintWorkpieceRepository, WorkpieceWriteError,
        )
        from src.robot_systems.paint.domain.workpieces.errors import WorkpieceReadError
        from src.engine.core.durable_files import sync_directory
        module = 'src.robot_systems.paint.domain.workpieces.repository.json_paint_workpiece_repository'
        with patch(module + '.generate_thumbnail_bytes', return_value=b'png'):
            repo = JsonPaintWorkpieceRepository(str(self.path.parent / 'paint'))
            record = Path(repo.save({'name': 'old'}))
            def sync_after_publish(path):
                if Path(path) == record.parent and json.loads(record.read_text())['name'] == 'new':
                    raise OSError('directory sync failed')
                return sync_directory(path)
            with patch(module + '.sync_directory', side_effect=sync_after_publish):
                with self.assertRaisesRegex(WorkpieceWriteError, 'durability unconfirmed'):
                    repo.update(record.parent.name, {'name': 'new'})
            self.assertTrue((record.parent / '.incomplete').exists())
            with self.assertRaises(WorkpieceWriteError):
                repo.load_raw(record.parent.name)
            with self.assertRaises(WorkpieceReadError):
                repo.list_for_matching()

    def test_strict_json_rejects_overflowed_float(self):
        from src.engine.repositories.json.json_store import read_json_object
        self.path.write_text('{"value":1e999}')
        with self.assertRaises(JsonStoreError):
            read_json_object(self.path)
