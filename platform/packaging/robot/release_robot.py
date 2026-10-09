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
ROBOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PLATFORM / 'packaging/shared'))
sys.path.insert(0, str(ROBOT))
import release_common as common
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gitea_release import GiteaPublisher

TESTS = (
    'tests.bootstrap.test_startup_config',
    'tests.bootstrap.test_ros_backend_launcher',
    'tests.robot_systems.paint.test_paint_system_overrides',
    'tests.engine.updates.test_release_targets',
    'tests.engine.updates.test_robot_release_workflow',
    'tests.engine.updates.test_gitea_release',
    'tests.engine.updates.test_robot_updates',
    'tests.engine.updates.test_update_service',
    'tests.engine.updates.test_installer_remote_support',
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
        self.run('Packaging integration tests', [sys.executable, '-B', PLATFORM / 'tests/packaging/test_packaging.py'])

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
            self.run(f'Build {kind}', [sys.executable, '-B', ROBOT / f'package_{kind}.py', self.target])
        self.run('Assemble exact component pair', [sys.executable, '-B', ROBOT / 'package_robot.py', self.target])

    def publish(self, remote, token, notes, signing_key=None):
        directory = common.ROOT / 'releases' / self.target / 'robot' / self.selected['release_version']
        manifest = json.loads((directory / 'manifest.json').read_text())
        if signing_key is not None:
            self.run('Sign complete robot manifest', ['openssl', 'dgst', '-sha256',
                     '-sign', signing_key, '-out', directory / 'manifest.json.sig',
                     directory / 'manifest.json'])
        if not manifest.get('source_svn_revision'):
            raise ValueError('Official release must record an SVN revision; rebuild after SVN publication')
        url = subprocess.check_output(['git', 'remote', 'get-url', '--push', remote], cwd=common.ROOT, text=True).strip()
        publisher = GiteaPublisher(url, token)
        self.run('Create/verify exact release tags', [sys.executable, '-B', ROBOT / 'tag_robot.py', self.target], cwd=common.ROOT)
        tags = [f'{self.target}/{kind}/v{identity["version"]}' for kind, identity in {**manifest['components'], 'robot': manifest}.items()]
        with tempfile.TemporaryDirectory(prefix='gitea-auth-') as temporary:
            askpass = Path(temporary) / 'askpass.py'
            askpass.write_text('#!' + sys.executable + '\nimport os, sys\nprint(os.environ["GITEA_USERNAME"] if "username" in sys.argv[1].lower() else os.environ["GITEA_TOKEN"])\n')
            askpass.chmod(0o700)
            env = {**self.env, 'GIT_ASKPASS': str(askpass), 'GIT_TERMINAL_PROMPT': '0',
                   'GITEA_USERNAME': publisher.username(), 'GITEA_TOKEN': token}
            self.run('Push source and release tags', ['git', '-c', 'credential.helper=', 'push', '--atomic', remote, 'HEAD:refs/heads/master', *['refs/tags/' + tag for tag in tags]], cwd=common.ROOT, env=env)
        release_url = publisher.publish(directory, manifest, notes, common.digest)
        self.report['release_url'] = release_url
        self.save()
        print(f'Published: {release_url}', flush=True)

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
            self.run('Install actual archive into temporary root', [sys.executable, '-B', bundle / 'install.py', '--root', root / 'installed', '--skip-system-setup'])
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
    parser.add_argument('action', choices=('check', 'build', 'verify', 'publish'), help='publish: SVN sync, tests, build/reuse, verify, tags, Gitea release')
    parser.add_argument('target', nargs='?', help='Defaults to robot_system in platform.json')
    parser.add_argument('--remote', default='gitea-test', help='Gitea Git remote for publication')
    parser.add_argument('--notes-file', type=Path, help='Optional release notes; otherwise generated from the manifest')
    parser.add_argument('--signing-key', type=Path, help='Sign manifest.json for trusted remote robot updates')
    parser.add_argument('--svn-synced', action='store_true', help='Actions mode: require SVN revision metadata instead of running git svn dcommit')
    args = parser.parse_args()
    workflow = None
    try:
        target = args.target or json.loads((PLATFORM / 'config/platform.json').read_text())['robot_system']
        selected = common.selection(target)
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
        report = PLATFORM / 'dist/release-checks' / f'{target}-{stamp}.json'
        workflow = Workflow(target, selected, report)
        workflow.report['action'] = args.action
        token = None
        notes = args.notes_file.read_text() if args.notes_file else f'Combined {target} robot release {selected["release_version"]}.'
        if args.action == 'publish':
            token = os.environ.get('GITEA_TOKEN')
            if not token:
                import getpass
                token = getpass.getpass('Gitea access token (repository write access): ')
            if not token:
                raise ValueError('Gitea access token is required')
            identity = common.source_identity()
            if args.svn_synced and not identity['source_svn_revision']:
                raise ValueError('Actions requires source published to SVN first; push the SVN-generated commit to Gitea')
            branch = subprocess.check_output(['git', 'branch', '--show-current'], cwd=common.ROOT, text=True).strip()
            if branch != 'master':
                raise ValueError('Publish from the shared master SVN work branch')
            url = subprocess.check_output(['git', 'remote', 'get-url', '--push', args.remote], cwd=common.ROOT, text=True).strip()
            publisher = GiteaPublisher(url, token)
            repository = publisher.request('GET', '')
            if repository is None:
                raise ValueError('Gitea repository does not exist or token cannot access it')
            if not repository.get('permissions', {}).get('push'):
                raise ValueError('Gitea token account needs repository write access')
            publisher.username()
            if not args.svn_synced:
                workflow.run('Publish pending commits to SVN', ['git', 'svn', 'dcommit'], cwd=common.ROOT)
        print(f'Target: {target}; robot {selected["release_version"]}; platform {selected["platform_version"]}; backend {selected["backend_version"]}\nReport: {report}', flush=True)
        with tempfile.TemporaryDirectory(prefix='robot-release-tests-') as temporary:
            workflow.env['MPLCONFIGDIR'] = temporary
            workflow.tests()
            directory = common.ROOT / 'releases' / target / 'robot' / selected['release_version']
            if args.action == 'build' or (args.action == 'publish' and not directory.exists()):
                workflow.build()
            if args.action in ('build', 'verify', 'publish'):
                workflow.verify()
            if args.action == 'publish':
                workflow.publish(args.remote, token, notes, args.signing_key)
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
