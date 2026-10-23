"""Persisted compound fixtures preserve all component geometry and states."""
from copy import deepcopy
from pathlib import Path
from threading import Lock
from types import SimpleNamespace
from concurrent.futures import Future
from unittest.mock import Mock
import sys
import pytest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from configuration.cell_scene import merge_cell_scene,validate_cell_scene
from configuration.domain import ConfigurationError,Conflict
from configuration.service import ConfigurationService
from configuration.repository import YamlProfileRepository
from safety.cell_scene_manager import CellSceneManager
from cell_scene_fakes import scene_node


def document():
    return {'CELL_COLLISION_OBJECTS':{f'cell_fixture_{name}':{'enabled':True,'frame':'mounting_surface',
        'size_mm':[10.+index,20.,30.], 'pose':[float(index*100),20.,30.,0.,0.,float(index*45)]}
        for index,name in enumerate(('one','two','three'))}}


class Runtime:
    def __init__(self,value):self.value=deepcopy(value)
    def snapshot(self,section):return deepcopy(self.value)
    def apply(self,section,value):self.value=deepcopy(value)


def test_merge_persists_group_and_disables_sources_across_restart(tmp_path):
    original=document()
    path=tmp_path/'cell_scene.yaml'
    path.write_text(yaml.safe_dump(original))
    runtime=Runtime(original)
    repository=YamlProfileRepository('tray',{'cell_scene':path},root=tmp_path)
    service=ConfigurationService(repository,runtime)
    view=service.get('cell_scene')
    result=service.update('cell_scene',{'merge':{'ids':['cell_fixture_one','cell_fixture_two'],
        'name':'dispenser'}},view['revision'])
    assert result['merged_object_id']=='cell_fixture_dispenser'
    definitions=result['saved']['CELL_COLLISION_OBJECTS']
    assert definitions['cell_fixture_dispenser']['parts']==[
        {key:original['CELL_COLLISION_OBJECTS'][identifier][key] for key in ('size_mm','pose')}
        for identifier in ('cell_fixture_one','cell_fixture_two')]
    assert definitions['cell_fixture_three']==original['CELL_COLLISION_OBJECTS']['cell_fixture_three']
    assert definitions['cell_fixture_one']['merged_into']=='cell_fixture_dispenser'
    assert not definitions['cell_fixture_one']['enabled']
    restarted=YamlProfileRepository('tray',{'cell_scene':path},root=tmp_path)
    assert restarted.read('cell_scene')==result['saved']
    with pytest.raises(Conflict):
        service.update('cell_scene',{'merge':{'ids':['cell_fixture_one','cell_fixture_two'],'name':'other'}},view['revision'])


def test_repeated_merge_flattens_geometry_and_preserves_all_sources():
    doc= document()
    first,_=merge_cell_scene(doc,{'ids':['cell_fixture_one','cell_fixture_two'],'name':'first'})
    second,identifier=merge_cell_scene(first,{'ids':['cell_fixture_first','cell_fixture_three'],'name':'all'})
    group=second['CELL_COLLISION_OBJECTS'][identifier]
    assert len(group['parts'])==3
    assert second['CELL_COLLISION_OBJECTS']['cell_fixture_first']['merged_into']==identifier
    assert validate_cell_scene(second)==second


@pytest.mark.parametrize('change', ['mixed_state','different_frame','duplicate_id','missing_id','existing_name','invalid_name','already_merged'])
def test_unsafe_or_ambiguous_merge_is_rejected_without_mutation(change):
    doc=document();ids=['cell_fixture_one','cell_fixture_two'];name='merged'
    if change=='mixed_state':doc['CELL_COLLISION_OBJECTS']['cell_fixture_two']['enabled']=False
    if change=='different_frame':doc['CELL_COLLISION_OBJECTS']['cell_fixture_two']['frame']='other'
    if change=='duplicate_id':ids=['cell_fixture_one','cell_fixture_one']
    if change=='missing_id':ids=['cell_fixture_one','cell_fixture_missing']
    if change=='existing_name':name='one'
    if change=='invalid_name':name='with spaces'
    if change=='already_merged':doc,_=merge_cell_scene(doc,{'ids':ids,'name':'previous'})
    original=deepcopy(doc)
    with pytest.raises(ConfigurationError):merge_cell_scene(doc,{'ids':ids,'name':name})
    assert doc==original


def test_moveit_diff_contains_one_compound_and_removes_original_objects():
    original=document()
    merged,identifier=merge_cell_scene(original,{'ids':['cell_fixture_one','cell_fixture_two'],'name':'dispenser'})
    node,requests,world=scene_node()
    manager=CellSceneManager(node,original)
    manager.initialize()
    before={obj.id:obj for obj in requests[-1].scene.world.collision_objects}
    manager.apply(merged)
    after={obj.id:obj for obj in requests[-1].scene.world.collision_objects}
    assert after['cell_fixture_one'].operation==after['cell_fixture_one'].REMOVE
    assert after['cell_fixture_two'].operation==after['cell_fixture_two'].REMOVE
    group=after[identifier]
    assert len(group.primitives)==len(group.primitive_poses)==2
    for index,old_id in enumerate(('cell_fixture_one','cell_fixture_two')):
        assert group.primitives[index]==before[old_id].primitives[0]
        assert group.primitive_poses[index]==before[old_id].primitive_poses[0]
    restarted=CellSceneManager(node,merged)
    restarted.initialize()
    fresh={obj.id:obj for obj in requests[-1].scene.world.collision_objects}
    assert 'cell_fixture_one' not in fresh
    assert 'cell_fixture_one' not in world
    assert len(fresh[identifier].primitives)==2
    disabled=deepcopy(merged);disabled['CELL_COLLISION_OBJECTS'][identifier]['enabled']=False
    manager.apply(disabled)
    last={obj.id:obj for obj in requests[-1].scene.world.collision_objects}
    assert last[identifier].operation==last[identifier].REMOVE
