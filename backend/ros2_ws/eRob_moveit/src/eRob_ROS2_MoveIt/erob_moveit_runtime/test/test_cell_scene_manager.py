"""Use actual ROS messages with an in-memory service client; no ROS node/hardware."""
from concurrent.futures import Future
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from safety.cell_scene_manager import CellSceneManager
from cell_scene_fakes import scene_node

DOCUMENT={'CELL_COLLISION_OBJECTS':{'cell_fixture_test':{'enabled':True,'frame':'mounting_surface',
    'size_mm':[10.,20.,30.],'pose':[50.,60.,70.,0.,0.,90.]}}}


def manager():
    node,calls,world=scene_node()
    return CellSceneManager(node,DOCUMENT),calls


def test_startup_and_toggle_preserve_shapes_frames_and_other_scene_data():
    scene,calls=manager()
    scene.initialize()
    assert scene.initialize()
    obj=calls[0].scene.world.collision_objects[0]
    assert obj.header.frame_id == 'mounting_surface'
    assert list(obj.primitives[0].dimensions) == [.01,.02,.03]
    assert abs(obj.primitive_poses[0].position.x-.05)<1e-9
    assert abs(obj.primitive_poses[0].orientation.z-2**-.5)<1e-9
    assert calls[0].scene.is_diff and calls[0].scene.robot_state.is_diff
    disabled=deepcopy(DOCUMENT)
    disabled['CELL_COLLISION_OBJECTS']['cell_fixture_test']['enabled']=False
    scene.apply(disabled)
    assert calls[-1].scene.world.collision_objects[0].operation == obj.REMOVE
    scene.apply(DOCUMENT)
    assert calls[-1].scene.world.collision_objects[0].operation == obj.ADD
    assert scene.snapshot() == DOCUMENT


def test_saved_disabled_fixture_stays_disabled_on_fresh_startup():
    scene,calls=manager()
    scene._document['CELL_COLLISION_OBJECTS']['cell_fixture_test']['enabled']=False
    scene.initialize()
    assert not calls[0].scene.world.collision_objects
    assert scene.snapshot()['CELL_COLLISION_OBJECTS']['cell_fixture_test']['enabled'] is False


def test_rejected_application_does_not_claim_saved_state_was_applied():
    import pytest
    scene,calls=manager()
    scene.initialize()
    failed=Future()
    failed.set_result(SimpleNamespace(success=False))
    scene._client.call_async.side_effect=lambda request:failed
    changed=deepcopy(DOCUMENT)
    changed['CELL_COLLISION_OBJECTS']['cell_fixture_test']['enabled']=False
    with pytest.raises(RuntimeError,match='rejected'):
        scene.apply(changed)
    assert scene.snapshot() is None
    assert not scene.is_ready()


def test_motion_is_held_until_cell_scene_application_is_confirmed():
    import ast
    from threading import Lock
    path=Path(__file__).resolve().parents[1]/'scripts/robot_controller.py'
    tree=ast.parse(path.read_text())
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='RobotController')
    method=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='is_hardware_ready_for_motion')
    namespace={}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method],type_ignores=[])),str(path),'exec'),namespace)
    scene,calls=manager()
    node=SimpleNamespace(cell_scene_manager=scene,_fake_hardware=True,_motion_interlock_lock=Lock(),
        _motion_interlock_active=False,_collision_recovery_hold=False,_collision_detection_suppressed=False)
    assert not namespace['is_hardware_ready_for_motion'](node)
    scene.initialize()
    assert namespace['is_hardware_ready_for_motion'](node)


def test_table_surface_is_unchanged_mesh_and_remains_in_every_diff():
    from unittest.mock import patch
    package=Path(__file__).resolve().parents[2]/'zeroerr'
    uri='package://zeroerr/meshes/cells/paint_tray_dry_compact/paint_tray_dry_compact.surface_3levels.stl'
    with patch('ament_index_python.packages.get_package_share_directory',return_value=str(package)):
        surface=CellSceneManager._load_surface(uri)
    assert len(surface.meshes[0].triangles)==10
    assert abs(min(point.z for point in surface.meshes[0].vertices)+.026)<1e-6
    scene,calls=manager()
    scene._surface=surface
    scene.initialize()
    disabled=deepcopy(DOCUMENT)
    disabled['CELL_COLLISION_OBJECTS']['cell_fixture_test']['enabled']=False
    scene.apply(disabled)
    assert calls[-1].scene.world.collision_objects[-1].id == surface.id
    assert calls[-1].scene.world.collision_objects[-1].operation == surface.ADD


def test_already_absent_disabled_fixture_is_idempotent():
    scene,calls=manager()
    scene.initialize()
    disabled=deepcopy(DOCUMENT)
    disabled['CELL_COLLISION_OBJECTS']['cell_fixture_test']['enabled']=False
    scene.apply(disabled)
    assert scene.is_ready()
    scene.apply(disabled)
    assert scene.is_ready()
    assert not calls[-1].scene.world.collision_objects


def test_startup_removes_disabled_fixture_only_if_it_exists():
    disabled=deepcopy(DOCUMENT)
    disabled['CELL_COLLISION_OBJECTS']['cell_fixture_test']['enabled']=False
    node,calls,world=scene_node(['cell_fixture_test','unrelated'])
    scene=CellSceneManager(node,disabled)
    scene.initialize()
    assert scene.is_ready()
    assert world=={'unrelated'}
    assert calls[0].scene.world.collision_objects[0].operation==calls[0].scene.world.collision_objects[0].REMOVE


def test_startup_query_failure_does_not_apply_or_unblock_motion():
    scene,calls=manager()
    original=scene._reader.call_async.side_effect
    failed=Future();failed.set_exception(RuntimeError('scene unavailable'))
    scene._reader.call_async.side_effect=lambda request:failed
    scene.initialize()
    assert not calls
    assert not scene.is_ready()
    assert scene._starting is None
    scene._reader.call_async.side_effect=original
    scene.initialize()
    assert scene.is_ready()


def test_unavailable_query_service_does_not_send_collision_changes():
    import pytest
    scene,calls=manager()
    scene.initialize()
    count=len(calls)
    scene._reader.service_is_ready.return_value=False
    with pytest.raises(RuntimeError,match='query is unavailable'):
        scene.apply(DOCUMENT)
    assert len(calls)==count
    assert scene.snapshot()==DOCUMENT
