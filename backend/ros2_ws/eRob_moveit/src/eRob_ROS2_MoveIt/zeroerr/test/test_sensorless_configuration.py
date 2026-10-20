"""Profile selection, GUI persistence and Python/C++ config parity without a robot."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE))
from zeroerr_configuration.sensorless_collision import (
    load_sensorless_config, profile_config_path, runtime_settings,
    read_monitor_config, write_monitor_config,
)
SHARED = PACKAGE/'config/shared/sensorless_collision.yaml'


class SensorlessConfigurationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.build = tempfile.TemporaryDirectory()
        directory = Path(cls.build.name)
        source = directory/'config.cpp'
        source.write_text('''#include "zeroerr/sensorless_configuration.hpp"
#include <iostream>
int main(int argc, char **argv) {
  try {
    if (argc == 3) zeroerr::save_sensorless_monitor_patch(argv[1], nlohmann::json::parse(argv[2]));
    std::cout << zeroerr::sensorless_json(zeroerr::load_sensorless_config(argv[1])).dump();
  } catch (const std::exception &e) {std::cerr << e.what(); return 1;}
}''')
        cls.binary = directory/'config'
        subprocess.run(['g++', '-std=c++17', '-Wall', '-Wextra', '-Werror',
                        '-I'+str(PACKAGE/'collision_detection/runtime/include'),
                        str(source), '-lyaml-cpp', '-o', str(cls.binary)], check=True, timeout=60)

    @classmethod
    def tearDownClass(cls):
        cls.build.cleanup()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.a = self.root/'a.yaml'
        self.b = self.root/'b.yaml'
        for path in (self.a, self.b):
            path.write_text(yaml.safe_dump({'RUNTIME_INCLUDES':[str(SHARED)]}))
        self.shared_bytes = SHARED.read_bytes()

    def cpp(self, path, patch=None):
        args = [str(self.binary), str(path)]
        if patch is not None: args.append(json.dumps(patch))
        return json.loads(subprocess.check_output(args, text=True))

    def test_all_profiles_have_matching_python_cpp_values(self):
        for path in PACKAGE.glob('config/*/sensorless_collision.yaml'):
            if path == SHARED: continue
            with self.subTest(profile=path.parent.name):
                self.assertEqual(load_sensorless_config(path), self.cpp(path))

    def test_python_gui_save_isolated_preserves_inherited_model_and_other_sections(self):
        original = load_sensorless_config(self.a)
        monitor = read_monitor_config(self.a)
        monitor['collision_sensitivity_percent'] = 125.0
        write_monitor_config(self.a, monitor)
        raw = yaml.safe_load(self.a.read_text())
        self.assertEqual(raw['monitor'], {'collision_sensitivity_percent':125.0})
        updated = load_sensorless_config(self.a)
        self.assertEqual(updated['controller'], original['controller'])
        self.assertEqual(updated['runtime'], original['runtime'])
        self.assertEqual(updated['monitor']['motion_model_fit'], original['monitor']['motion_model_fit'])
        self.assertEqual(load_sensorless_config(self.b), original)
        self.assertEqual(SHARED.read_bytes(), self.shared_bytes)
        self.assertEqual(updated, self.cpp(self.a))

    def test_cpp_gui_patch_isolated_and_python_reads_applied_values(self):
        self.cpp(self.a, {'confirm_duration_ms':75.0,'external_torque_thresholds':[1.,2.,3.,4.,5.,6.]})
        raw = yaml.safe_load(self.a.read_text())
        self.assertEqual(set(raw['monitor']), {'confirm_duration_ms','external_torque_thresholds'})
        self.assertEqual(read_monitor_config(self.a)['confirm_duration_ms'],75.0)
        self.assertEqual(read_monitor_config(self.b)['confirm_duration_ms'],50.0)
        self.assertEqual(SHARED.read_bytes(),self.shared_bytes)

    def test_restoring_shared_value_removes_override_in_both_writers(self):
        self.cpp(self.a, {'confirm_duration_ms':75.0})
        self.cpp(self.a, {'confirm_duration_ms':50.0})
        self.assertNotIn('monitor',yaml.safe_load(self.a.read_text()))
        monitor = read_monitor_config(self.a)
        monitor['confirm_duration_ms']=75.0
        write_monitor_config(self.a,monitor)
        monitor['confirm_duration_ms']=50.0
        write_monitor_config(self.a,monitor)
        self.assertNotIn('monitor',yaml.safe_load(self.a.read_text()))

    def test_nested_profile_overrides_preserve_unmodified_controller_and_model_fields(self):
        self.a.write_text(yaml.safe_dump({'RUNTIME_INCLUDES':[str(SHARED)],
            'controller':{'warmup_sec':4.0},'runtime':{'EXECUTOR_COLLISION_STOP_STRATEGY':'planned_path'},
            'monitor':{'dynamic_threshold_coefficients':{'Joint_5':[0.0]*9}}}))
        data=load_sensorless_config(self.a)
        self.assertEqual(data['controller']['warmup_sec'],4.0)
        self.assertEqual(data['controller']['observer_gain'],10.0)
        self.assertIn('Joint_1',data['monitor']['dynamic_threshold_coefficients'])
        self.assertEqual(data,self.cpp(self.a))

    def test_fitting_one_joint_saves_only_that_joint_override(self):
        monitor = read_monitor_config(self.a)
        monitor['dynamic_threshold_coefficients']['Joint_5'] = [0.0]*9
        write_monitor_config(self.a, monitor)
        raw=yaml.safe_load(self.a.read_text())
        self.assertEqual(raw['monitor'], {'dynamic_threshold_coefficients':{'Joint_5':[0.0]*9}})
        self.assertEqual(read_monitor_config(self.a), monitor)
        self.assertEqual(load_sensorless_config(self.a), self.cpp(self.a))

    def test_unknown_profile_never_silently_falls_back(self):
        with self.assertRaises(FileNotFoundError):profile_config_path(PACKAGE,'missing_profile')
        for name in ('../paint','', 'a/b'):
            with self.assertRaises(ValueError):profile_config_path(PACKAGE,name)

    def test_environment_profile_selection_and_runtime_aliases(self):
        with patch.dict(os.environ,{'ZEROERR_ACTIVE_PROFILE':'paint'}):
            self.assertEqual(profile_config_path(PACKAGE).parent.name,'paint')
        values=runtime_settings(PACKAGE,'development_short_links')
        self.assertEqual(values['EXECUTOR_COLLISION_STOP_STRATEGY'],'measured_ruckig')
        self.assertFalse(values['COLLISION_RESET_RECALIBRATE_ON_RELEASE'])
        self.assertIn('/development_short_links/',values['SENSORLESS_COLLISION_CONFIG_PATH'])

    def test_cycle_and_schema_errors_refused_by_python_and_cpp(self):
        for data in ({'RUNTIME_INCLUDES':['a.yaml']}, {'schema_version':999,'controller':{},'monitor':{},'runtime':{}}):
            self.a.write_text(yaml.safe_dump(data))
            with self.assertRaises(ValueError):load_sensorless_config(self.a)
            result=subprocess.run([str(self.binary),str(self.a)],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)


if __name__=='__main__':unittest.main()
