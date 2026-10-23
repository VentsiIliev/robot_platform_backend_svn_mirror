"""Configuration transport never writes local robot-profile files."""
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scene_editor.backend_configuration import BackendConfigurationClient, cell_fixture_identifier


class BackendConfigurationTests(unittest.TestCase):
    def test_merge_sends_ids_and_name_with_fresh_revision(self):
        client=BackendConfigurationClient('http://localhost:5000')
        view=self.view()
        result=self.view()
        result['merged_object_id']='cell_fixture_dispenser'
        result['saved']['CELL_COLLISION_OBJECTS']={'cell_fixture_dispenser':{'enabled':True,'parts':[]}}
        with patch.object(client,'get',return_value=view), patch.object(client,'_request',return_value=result) as request:
            client.merge_fixtures(['cell_fixture_one','cell_fixture_two'],'dispenser')
        request.assert_called_once_with('PATCH',body={'expected_revision':'r1',
            'changes':{'merge':{'ids':['cell_fixture_one','cell_fixture_two'],'name':'dispenser'}}})

    def test_scene_identifiers_only_accept_independent_equipment_objects(self):
        self.assertEqual(cell_fixture_identifier('world/cell_fixture_tray_01/0'), 'cell_fixture_tray_01')
        for value in ('robot/mounting_surface/collision/0', 'world/cell_surface_tray/0',
                      'attached/cell_fixture_tray_01/0', 'world/cell_fixture_tray_01/1', None):
            self.assertIsNone(cell_fixture_identifier(value))

    def test_direct_action_reads_revision_and_changes_only_selected_object(self):
        view = self.view()
        view['saved']['CELL_COLLISION_OBJECTS'] = {'cell_fixture_tray_01':{'enabled':True},
                                                  'cell_fixture_tray_02':{'enabled':True}}
        client = BackendConfigurationClient('http://localhost:5000')
        with patch.object(client, 'get', return_value=view), patch.object(client, 'save') as save:
            client.set_enabled('cell_fixture_tray_01', False)
        save.assert_called_once_with('r1', {'cell_fixture_tray_01':False})
        with patch.object(client, 'get', return_value=view), patch.object(client, 'save') as save:
            with self.assertRaisesRegex(ValueError, 'not configured'):
                client.set_enabled('missing', False)
        save.assert_not_called()

    def test_unchanged_direct_state_retries_only_pending_application(self):
        view = self.view(True)
        view['saved']['CELL_COLLISION_OBJECTS'] = {'cell_fixture_tray_01':{'enabled':False}}
        client = BackendConfigurationClient('http://localhost:5000')
        with patch.object(client,'get',return_value=view), patch.object(client,'apply') as apply, patch.object(client,'save') as save:
            client.set_enabled('cell_fixture_tray_01', False)
        apply.assert_called_once_with('r1')
        save.assert_not_called()

    def view(self, pending=False):
        return {'success':True,'profile':'paint_tray_dry','revision':'r1',
                'saved':{'CELL_COLLISION_OBJECTS':{}},'pending_application':pending}

    def response(self, value):
        return io.BytesIO(json.dumps(value).encode())

    def test_save_uses_loaded_revision_and_only_enabled_changes(self):
        client=BackendConfigurationClient('http://localhost:5000/')
        with patch('scene_editor.backend_configuration.urlopen',return_value=self.response(self.view(True))) as call:
            result=client.save('original',{'cell_fixture_tray_01':False})
        self.assertTrue(result['pending_application'])
        request=call.call_args.args[0]
        self.assertEqual(request.method,'PATCH')
        self.assertEqual(request.full_url,'http://localhost:5000/configuration/cell_scene')
        self.assertEqual(json.loads(request.data),{'expected_revision':'original',
            'changes':{'CELL_COLLISION_OBJECTS':{'cell_fixture_tray_01':{'enabled':False}}}})

    def test_conflict_is_reported_without_automatic_retry(self):
        error=HTTPError('http://localhost',409,'Conflict',{},self.response({'error':'Configuration changed; reload'}))
        with patch('scene_editor.backend_configuration.urlopen',side_effect=error) as call:
            with self.assertRaisesRegex(RuntimeError,'reload'):
                BackendConfigurationClient('http://localhost:5000').save('old',{'cell_fixture_tray_01':False})
        self.assertEqual(call.call_count,1)

    def test_apply_reuses_saved_revision(self):
        with patch('scene_editor.backend_configuration.urlopen',return_value=self.response(self.view())) as call:
            BackendConfigurationClient('http://localhost:5000').apply('saved')
        request=call.call_args.args[0]
        self.assertEqual(request.method,'POST')
        self.assertTrue(request.full_url.endswith('/cell_scene/apply'))
        self.assertEqual(json.loads(request.data),{'expected_revision':'saved'})

    def test_invalid_responses_and_urls_are_rejected(self):
        for url in ('file:///tmp/settings','http://user:password@localhost','http://localhost?query'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                BackendConfigurationClient(url)
        with patch('scene_editor.backend_configuration.urlopen',return_value=self.response({'success':True})):
            with self.assertRaisesRegex(RuntimeError,'invalid'):
                BackendConfigurationClient('http://localhost:5000').get()


if __name__=='__main__':unittest.main()
