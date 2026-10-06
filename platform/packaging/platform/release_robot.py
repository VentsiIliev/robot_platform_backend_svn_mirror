#!/usr/bin/env python3
"""Test, build and verify the configured combined robot release without hardware."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

PLATFORM = Path(__file__).resolve().parents[2]
DEPLOYMENT = PLATFORM.parent / 'deployment/scripts'
sys.path.insert(0, str(DEPLOYMENT))
import release_common as common

TESTS = (
    'tests.bootstrap.test_startup_config',
    'tests.bootstrap.test_ros_backend_launcher',
    'tests.robot_systems.paint.test_paint_system_overrides',
    'tests.engine.updates.test_release_targets',
    'tests.engine.updates.test_robot_release_workflow',
)


class Workflow:
    def __init__(self, target, selected, report):
        self.target = target
        self.selected = selected
        self.report_path = report
        self.report = dict(target=target, selection=selected, status='running', stages=[])
        self.env = dict(os.environ)
        for key in ('PYTHONPATH', 'PYTHONHOME'):
            self.env.pop(key, None)
        self.env.update(PYTHONDONTWRITEBYTECODE='1', QT_QPA_PLATFORM='offscreen')

    def save(self):
        self.report_path.parent.mkdir(parents=True, exist_ok=True)
        common.write_json(self.report_path, self.report)

    def run(self, label, command, cwd=PLATFORM, env=None):
        print(f'\n[{label}]', flush=True)
        stage = dict(name=label, command=[str(part) for part in command], status='running')
        self.report['stages'].append(stage)
        self.save()
        started = time.monotonic()
        try:
            subprocess.run(stage['command'], cwd=cwd, env=env or self.env, check=True)
            stage['status'] = 'passed'
        except BaseException:
            stage['status'] = 'failed'
            raise
        finally:
            stage['seconds'] = round(time.monotonic() - started, 2)
            self.save()

    def tests(self):
        python = PLATFORM / '.venv/bin/python'
        if not python.is_file():
            raise ValueError(f'Missing platform environment: {python}')
        self.run('Platform release tests', [python, '-B', '-m', 'unittest', *TESTS, '-q'])
        self.run('Packaging integration tests', [sys.executable, '-B', DEPLOYMENT / 'test_packaging.py'])

    def build(self):
        common.source_identity()  # Preserve the official packagers' clean-source gate.
        output = common.ROOT / 'releases' / self.target / 'robot' / self.selected['release_version']
        if output.exists():
            raise ValueError(f'Release already exists: {output}. Use verify or select a new version.')
        missing = []
        for kind in ('backend', 'platform'):
            directory = common.ROOT / 'releases' / self.target / kind / self.selected[kind + '_version']
            if directory.exists():
                common.component(self.target, kind, self.selected)
                print(f'Reusing validated {kind} {self.selected[kind + "_version"]}', flush=True)
            else:
                missing.append(kind)
        for kind in missing:
            self.run(f'Build {kind}', [sys.executable, '-B', DEPLOYMENT / f'package_{kind}.py', self.target])
        self.run('Assemble exact component pair', [sys.executable, '-B', DEPLOYMENT / 'package_robot.py', self.target])

    def verify(self):
        directory = common.ROOT / 'releases' / self.target / 'robot' / self.selected['release_version']
        manifest = json.loads((directory / 'manifest.json').read_text())
        if (manifest.get('component'), manifest.get('target'), manifest.get('version'), manifest.get('selection')) != (
            'robot', self.target, self.selected['release_version'], self.selected
        ):
            raise ValueError('Combined release manifest does not match the configured selection')
        name = manifest['archive']
        if Path(name).name != name:
            raise ValueError('Invalid robot archive name')
        archive = directory / name
        if common.digest(archive) != manifest['sha256']:
            raise ValueError('Combined release checksum mismatch')
        with tempfile.TemporaryDirectory(prefix='robot-release-check-') as temporary:
            root = Path(temporary)
            common.extract(archive, root / 'extracted')
            bundle = root / 'extracted/robot'
            embedded = json.loads((bundle / 'manifest.json').read_text())
            expected = {key: value for key, value in manifest.items() if key not in ('archive', 'sha256')}
            if embedded != expected:
                raise ValueError('Robot archive manifest differs from published manifest')
            self.run('Install actual archive into temporary root', [sys.executable, '-B', bundle / 'install.py', '--root', root / 'installed'])
            executable = manifest['components']['platform']['executable']
            if Path(executable).name != executable:
                raise ValueError('Invalid platform executable name')
            env = {**self.env, 'MPLCONFIGDIR': str(root / 'mpl')}
            self.run('Installed frozen self-test', [root / 'installed/launch.sh', '--self-test'], cwd=root, env=env)
        self.report['archive'] = str(archive)
        self.report['sha256'] = manifest['sha256']
        self.save()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('check', 'build', 'verify'), help='check: tests only; build: tests/build/install check; verify: tests/existing archive install check')
    parser.add_argument('target', nargs='?', help='Defaults to robot_system in platform.json')
    args = parser.parse_args()
    workflow = None
    try:
        target = args.target or json.loads((PLATFORM / 'config/platform.json').read_text())['robot_system']
        selected = common.selection(target)
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
        report = PLATFORM / 'dist/release-checks' / f'{target}-{stamp}.json'
        workflow = Workflow(target, selected, report)
        workflow.report['action'] = args.action
        print(f'Target: {target}; robot {selected["release_version"]}; platform {selected["platform_version"]}; backend {selected["backend_version"]}\nReport: {report}', flush=True)
        with tempfile.TemporaryDirectory(prefix='robot-release-tests-') as temporary:
            workflow.env['MPLCONFIGDIR'] = temporary
            workflow.tests()
            if args.action == 'build':
                workflow.build()
            if args.action in ('build', 'verify'):
                workflow.verify()
        workflow.report['status'] = 'passed'
        workflow.save()
        print(f'\n{args.action} passed. Report: {report}')
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError, KeyboardInterrupt) as exc:
        if workflow:
            workflow.report.update(status='failed', error=str(exc))
            workflow.save()
        parser.exit(1, f'\nRelease workflow failed: {exc}\n')


if __name__ == '__main__':
    main()
