from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np

from src.robot_systems.paint.domain.workpieces.repository.json_paint_workpiece_repository import (
    JsonPaintWorkpieceRepository,
    WorkpieceWriteError,
    _numpy_to_python,
)
from src.robot_systems.paint.domain.workpieces.service.paint_workpiece_service import (
    PaintWorkpieceService,
)


class TestNumpyToPython(unittest.TestCase):
    def test_converts_arrays_recursively(self) -> None:
        converted = _numpy_to_python(
            {
                "arr": np.array([[1, 2], [3, 4]]),
                "nested": [{"value": np.array([5.0, 6.0])}],
            }
        )

        self.assertEqual(converted["arr"], [[1, 2], [3, 4]])
        self.assertEqual(converted["nested"][0]["value"], [5.0, 6.0])


class TestJsonPaintWorkpieceRepository(unittest.TestCase):
    def test_save_list_load_update_thumbnail_delete_and_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with patch(
                "src.robot_systems.paint.domain.workpieces.repository.json_paint_workpiece_repository.generate_thumbnail_bytes",
                side_effect=[b"png", b"png2", b"regen"],
            ), patch(
                "src.robot_systems.paint.domain.workpieces.repository.json_paint_workpiece_repository.datetime"
            ) as dt:
                fixed_now = MagicMock()
                fixed_now.strftime.side_effect = [
                    "2026-05-06",
                    "2026-05-06_12-00-00-000001",
                ]
                dt.now.return_value = fixed_now
                repo = JsonPaintWorkpieceRepository(tmp)

                saved_path = repo.save(
                    {
                        "workpieceId": "wp-1",
                        "name": "Original",
                        "contour": np.array([[[1.0, 2.0]]]),
                    }
                )

                self.assertTrue(saved_path.endswith("_workpiece.json"))
                saved_file = Path(saved_path)
                self.assertTrue(saved_file.exists())
                saved_data = json.loads(saved_file.read_text(encoding="utf-8"))
                self.assertEqual(saved_data["contour"], [[[1.0, 2.0]]])

                records = repo.list_all()
                self.assertEqual(len(records), 1)
                self.assertEqual(records[0]["id"], "2026-05-06_12-00-00-000001")
                self.assertEqual(records[0]["name"], "Original")
                self.assertTrue(records[0]["thumbnail_path"].endswith("_thumbnail.png"))

                storage_id = records[0]["id"]
                self.assertEqual(repo.load_raw(storage_id)["workpieceId"], "wp-1")
                self.assertTrue(repo.workpiece_id_exists("wp-1"))
                self.assertFalse(repo.workpiece_id_exists("missing"))

                updated_path = repo.update(
                    storage_id,
                    {"workpieceId": "wp-1", "name": "Updated"},
                )
                self.assertEqual(updated_path, saved_path)
                self.assertEqual(repo.load_raw(storage_id)["name"], "Updated")

                thumb_path = saved_file.parent / f"{storage_id}_thumbnail.png"
                self.assertEqual(repo.get_thumbnail_bytes(storage_id), b"png2")
                thumb_path.unlink()
                self.assertEqual(repo.get_thumbnail_bytes(storage_id), b"regen")
                self.assertTrue(thumb_path.exists())

                self.assertTrue(repo.delete(storage_id))
                self.assertFalse(repo.delete(storage_id))
                self.assertIsNone(repo.load_raw(storage_id))
                self.assertIsNone(repo.get_thumbnail_bytes(storage_id))

    def test_preparation_failures_preserve_existing_pair_and_hide_new_records(self):
        module = "src.robot_systems.paint.domain.workpieces.repository.json_paint_workpiece_repository"
        with tempfile.TemporaryDirectory() as tmp:
            repo = JsonPaintWorkpieceRepository(tmp)
            with patch(module + ".generate_thumbnail_bytes", return_value=b"original thumbnail"):
                path = Path(repo.save({"name": "original"}))
            storage_id = path.parent.name
            thumb = path.parent / (storage_id + "_thumbnail.png")
            original = path.read_bytes(), thumb.read_bytes()
            for payload, thumbnail in [({"bad": object()}, b"png"), ({"name": "new"}, None), ({"name": "new"}, b"")]:
                with self.subTest(payload=payload, thumbnail=thumbnail), patch(module + ".generate_thumbnail_bytes", return_value=thumbnail):
                    with self.assertRaises(WorkpieceWriteError):
                        repo.update(storage_id, payload)
                    with self.assertRaises(WorkpieceWriteError):
                        repo.save(payload)
                    self.assertEqual((path.read_bytes(), thumb.read_bytes()), original)
                    self.assertEqual(len(repo.list_all()), 1)
                    self.assertEqual(list(Path(tmp).rglob('.paint-*')), [])
            with patch(module + ".generate_thumbnail_bytes", side_effect=RuntimeError("encoder failed")):
                ok, message = PaintWorkpieceService(repo).update(storage_id, {"name": "new"})
                self.assertFalse(ok)
                self.assertIn(storage_id, message)
                self.assertIn("Thumbnail generation failed: encoder failed", message)

    def test_json_publication_failure_restores_thumbnail(self):
        import os
        module = "src.robot_systems.paint.domain.workpieces.repository.json_paint_workpiece_repository"
        with tempfile.TemporaryDirectory() as tmp, patch(module + ".generate_thumbnail_bytes", return_value=b"original"):
            repo = JsonPaintWorkpieceRepository(tmp)
            path = Path(repo.save({"name": "original"}))
            storage_id = path.parent.name
            thumb = path.parent / (storage_id + "_thumbnail.png")
            original = path.read_bytes(), thumb.read_bytes()
            replace = os.replace
            def fail_json(source, destination):
                if str(destination) == str(path):
                    raise OSError("JSON publication failed")
                return replace(source, destination)
            with patch(module + ".generate_thumbnail_bytes", return_value=b"new"), patch(module + ".os.replace", side_effect=fail_json):
                with self.assertRaisesRegex(WorkpieceWriteError, "JSON publication failed"):
                    repo.update(storage_id, {"name": "new"})
            self.assertEqual((path.read_bytes(), thumb.read_bytes()), original)
            self.assertEqual(len(repo.list_all()), 1)
            self.assertFalse((path.parent / '.incomplete').exists())
            self.assertEqual(list(path.parent.glob('.paint-*')), [])

    def test_failed_rollback_blocks_record_and_preserves_recovery_files(self):
        import os
        module = "src.robot_systems.paint.domain.workpieces.repository.json_paint_workpiece_repository"
        with tempfile.TemporaryDirectory() as tmp, patch(module + ".generate_thumbnail_bytes", return_value=b"original"):
            repo = JsonPaintWorkpieceRepository(tmp)
            path = Path(repo.save({"name": "original"}))
            storage_id = path.parent.name
            replace = os.replace
            calls = 0
            def fail_after_thumbnail(source, destination):
                nonlocal calls
                calls += 1
                if calls > 1:
                    raise OSError("disk unavailable")
                return replace(source, destination)
            with patch(module + ".os.replace", side_effect=fail_after_thumbnail):
                with self.assertRaisesRegex(WorkpieceWriteError, "rollback failed.*Record is blocked"):
                    repo.update(storage_id, {"name": "new"})
            self.assertEqual(repo.list_all(), [])
            with self.assertRaisesRegex(WorkpieceWriteError, "recovery is required"):
                repo.load_raw(storage_id)
            staging = Path((path.parent / '.incomplete').read_text())
            self.assertEqual((staging / 'previous_thumbnail.png').read_bytes(), b"original")

    def test_update_write_and_thumbnail_publication_failures_preserve_pair(self):
        module = "src.robot_systems.paint.domain.workpieces.repository.json_paint_workpiece_repository"
        with tempfile.TemporaryDirectory() as tmp, patch(module + ".generate_thumbnail_bytes", return_value=b"png"):
            repo = JsonPaintWorkpieceRepository(tmp)
            path = Path(repo.save({"name": "original"}))
            storage_id = path.parent.name
            thumb = path.parent / (storage_id + '_thumbnail.png')
            original = path.read_bytes(), thumb.read_bytes()
            for operation in ('os.fsync', 'os.replace'):
                with self.subTest(operation=operation), patch(module + '.' + operation, side_effect=OSError("disk failure")):
                    with self.assertRaisesRegex(WorkpieceWriteError, "disk failure"):
                        repo.update(storage_id, {"name": "new"})
                self.assertEqual((path.read_bytes(), thumb.read_bytes()), original)
                self.assertFalse((path.parent / '.incomplete').exists())

    def test_real_thumbnail_failure_does_not_publish_invalid_workpiece(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = JsonPaintWorkpieceRepository(tmp)
            with self.assertRaisesRegex(WorkpieceWriteError, "Thumbnail generation failed"):
                repo.save({"name": "missing contour"})
            self.assertEqual(repo.list_all(), [])
            path = repo.save({"name": "valid", "contour": [[0, 0], [10, 0], [10, 10]]})
            storage_id = Path(path).parent.name
            self.assertTrue(repo.get_thumbnail_bytes(storage_id).startswith(b'\x89PNG'))

    def test_staging_write_and_new_publication_failures_leave_no_record(self):
        module = "src.robot_systems.paint.domain.workpieces.repository.json_paint_workpiece_repository"
        with tempfile.TemporaryDirectory() as tmp, patch(module + ".generate_thumbnail_bytes", return_value=b"png"):
            repo = JsonPaintWorkpieceRepository(tmp)
            for operation in ('os.fsync', 'os.rename'):
                with self.subTest(operation=operation), patch(module + '.' + operation, side_effect=OSError("disk failure")):
                    with self.assertRaisesRegex(WorkpieceWriteError, "disk failure"):
                        repo.save({"name": "new"})
                    self.assertEqual(repo.list_all(), [])
                    self.assertEqual(list(Path(tmp).rglob('.paint-*')), [])

    def test_list_all_skips_invalid_entries_and_missing_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = JsonPaintWorkpieceRepository(tmp)
            date_dir = Path(tmp) / "2026-05-06"
            (date_dir / "missing").mkdir(parents=True)
            bad_dir = date_dir / "bad"
            bad_dir.mkdir(parents=True)
            (bad_dir / "bad_workpiece.json").write_text("{bad json", encoding="utf-8")

            self.assertEqual(repo.list_all(), [])

    def test_update_missing_storage_id_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = JsonPaintWorkpieceRepository(tmp)
            with self.assertRaisesRegex(FileNotFoundError, "not found"):
                repo.update("missing", {"name": "x"})


class TestPaintWorkpieceService(unittest.TestCase):
    def test_service_delegates_success_paths(self) -> None:
        repo = MagicMock()
        repo.save.return_value = "/tmp/file.json"
        repo.list_all.return_value = [{"id": "a"}]
        repo.delete.return_value = True
        repo.get_thumbnail_bytes.return_value = b"img"
        repo.workpiece_id_exists.return_value = True
        repo.update.return_value = "/tmp/file.json"
        repo.load_raw.return_value = {"name": "x"}
        service = PaintWorkpieceService(repo)

        self.assertEqual(service.save({"name": "x"}), (True, "/tmp/file.json"))
        self.assertEqual(service.list_all(), [{"id": "a"}])
        self.assertEqual(service.delete("a"), (True, "Deleted"))
        self.assertEqual(service.get_thumbnail_bytes("a"), b"img")
        self.assertTrue(service.workpiece_id_exists("wp-1"))
        self.assertEqual(service.update("a", {"name": "y"}), (True, "/tmp/file.json"))
        self.assertEqual(service.load_raw("a"), {"name": "x"})

    def test_load_exposes_matchable_saved_workpiece(self) -> None:
        repo = MagicMock()
        repo.load_raw.return_value = {
            "name": "Paint part",
            "workpieceId": "wp-1",
            "contour": [[0, 0], [10, 0], [10, 10]],
            "matchingContour": [[1, 1], [9, 1], [9, 9]],
        }
        workpiece = PaintWorkpieceService(repo).load("storage-1")

        self.assertEqual(workpiece.storage_id, "storage-1")
        self.assertEqual(workpiece.name, "Paint part")
        self.assertEqual(workpiece.get_main_contour().tolist(), [[1, 1], [9, 1], [9, 9]])

    def test_load_skips_workpieces_without_contour(self) -> None:
        repo = MagicMock()
        repo.load_raw.return_value = {"name": "Incomplete"}

        self.assertIsNone(PaintWorkpieceService(repo).load("storage-1"))

    def test_service_handles_repository_failures(self) -> None:
        repo = MagicMock()
        repo.save.side_effect = RuntimeError("save failed")
        repo.list_all.side_effect = RuntimeError("list failed")
        repo.delete.side_effect = RuntimeError("delete failed")
        repo.get_thumbnail_bytes.side_effect = RuntimeError("thumb failed")
        repo.workpiece_id_exists.side_effect = RuntimeError("exists failed")
        repo.update.side_effect = RuntimeError("update failed")
        repo.load_raw.side_effect = RuntimeError("load failed")
        service = PaintWorkpieceService(repo)

        self.assertEqual(service.save({}), (False, "save failed"))
        self.assertEqual(service.list_all(), [])
        self.assertEqual(service.delete("a"), (False, "delete failed"))
        self.assertIsNone(service.get_thumbnail_bytes("a"))
        self.assertFalse(service.workpiece_id_exists("wp-1"))
        self.assertEqual(service.update("a", {}), (False, "update failed"))
        self.assertIsNone(service.load_raw("a"))

    def test_delete_reports_not_found_when_repository_returns_false(self) -> None:
        repo = MagicMock()
        repo.delete.return_value = False
        service = PaintWorkpieceService(repo)

        self.assertEqual(service.delete("missing"), (False, "Workpiece 'missing' not found"))


if __name__ == "__main__":
    unittest.main()
