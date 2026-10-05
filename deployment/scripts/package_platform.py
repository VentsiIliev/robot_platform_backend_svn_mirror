#!/usr/bin/env python3
"""Build a versioned platform component selected by platform.json."""
import argparse
import os
from pathlib import Path
import platform
import subprocess
import tempfile

from release_common import ROOT, selection, source_identity, write_json, digest, archive_bundle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('target')
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    try:
        selected = selection(args.target)
        identity = {} if args.verify_only else source_identity()
        output = ROOT / 'releases' / args.target / 'platform' / selected['platform_version']
        if output.exists() and not args.verify_only:
            raise ValueError(f'Release already exists: {output}')
        executable = ROOT / 'platform/.venv/bin/python'
        if not executable.is_file():
            raise ValueError(f'Missing platform build environment: {executable}')
        env = dict(os.environ)
        for key in ('PYTHONPATH', 'PYTHONHOME'):
            env.pop(key, None)
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        subprocess.run([str(executable), 'packaging/platform/build.py', args.target], cwd=ROOT / 'platform', env=env, check=True)
        import sys
        sys.path.insert(0, str(ROOT / 'platform/packaging/platform'))
        from targets import load_target
        target = load_target(args.target)
        bundle = ROOT / 'platform/dist' / target['product']
        env.update(QT_QPA_PLATFORM='offscreen', MPLCONFIGDIR='/tmp/robot-release-mpl')
        subprocess.run([str(bundle / target['executable']), '--self-test'], env=env, check=True)
        if args.verify_only:
            print('Platform build and self-test passed; no release created')
            return
        manifest = dict(format=1, component='platform', target=args.target, version=selected['platform_version'],
                        backend=selected['backend'], profile=selected['backend_profile'], robot_driver=selected['robot_driver'],
                        architecture=platform.machine(), os='ubuntu-24.04', executable=target['executable'], **identity)
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=output.parent, prefix='.release-') as temporary:
            staging = Path(temporary)
            archive = staging / f'{args.target}-platform-{selected["platform_version"]}-{platform.machine()}.tar.gz'
            archive_bundle(bundle, archive, 'platform')
            manifest.update(archive=archive.name, sha256=digest(archive))
            write_json(staging / 'manifest.json', manifest)
            (staging / (archive.name + '.sha256')).write_text(f'{manifest["sha256"]}  {archive.name}\n')
            staging.rename(output)
        print(output)
    except (ValueError, RuntimeError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
