"""Real LFS projection and fast-forward publishing against a disposable local remote."""
import contextlib
import hashlib
import io
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts.github_lfs_mirror import MirrorError, oversized_blobs, publish_github_mirror


def git(root, *args):
    result = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=True,
                            env=dict(os.environ, GIT_LFS_SKIP_SMUDGE="1"))
    return result.stdout.strip()


@unittest.skipUnless(subprocess.run(["git", "lfs", "version"], capture_output=True).returncode == 0,
                     'Git LFS is required for mirror integration tests')
class GithubLfsMirrorTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        root = Path(self.directory.name)
        self.source, self.remote = root/'source', root/'remote.git'
        self.source.mkdir()
        git(self.source, 'init', '-b', 'master')
        git(self.source, 'config', 'user.name', 'Mirror Test')
        git(self.source, 'config', 'user.email', 'test@example.invalid')
        git(self.source, 'config', 'commit.gpgsign', 'false')
        (self.source/'code.py').write_text('original code\n')
        self.commit(1)
        git(root, 'init', '--bare', str(self.remote))
        git(self.source, 'remote', 'add', 'github-svn-mirror', str(self.remote))
        git(self.source, 'push', 'github-svn-mirror', 'master')
        self.original_remote = git(self.source, 'rev-parse', 'HEAD')
        self.payload = b'solid example\n' + b'x'*4096 + b'\nendsolid\n'
        (self.source/'fixture.stl').write_bytes(self.payload)
        (self.source/'code.py').write_text('updated code\n')
        self.commit(2)

    def commit(self, revision):
        git(self.source, 'add', '--all')
        git(self.source, 'commit', '-m', f'Revision {revision}\n\ngit-svn-id: https://example.invalid/svn/trunk@{revision} uuid')
        git(self.source, 'update-ref', 'refs/remotes/git-svn', git(self.source, 'rev-parse', 'HEAD'))

    def publish(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return publish_github_mirror(self.source, 'github-svn-mirror', limit=1024)

    def test_migrates_assets_preserves_source_and_repeatably_fast_forwards(self):
        source_head = git(self.source, 'rev-parse', 'HEAD')
        # Dirty files must never be used to construct the published tree.
        (self.source/'code.py').write_text('unrelated working edit\n')
        before_status = git(self.source, 'status', '--porcelain')
        result = self.publish()
        self.assertEqual(result.source_head, source_head)
        self.assertNotEqual(result.mirror_head, source_head)
        self.assertEqual(git(self.source, 'rev-parse', 'HEAD'), source_head)
        self.assertEqual(git(self.source, 'rev-parse', 'refs/remotes/git-svn'), source_head)
        self.assertEqual(git(self.source, 'status', '--porcelain'), before_status)
        self.assertEqual((self.source/'fixture.stl').read_bytes(), self.payload)
        self.assertEqual(git(self.remote, 'show', 'master:code.py'), 'updated code')
        self.assertEqual(oversized_blobs(self.remote, 'master', 1024), [])
        pointer = git(self.remote, 'show', 'master:fixture.stl')
        digest = hashlib.sha256(self.payload).hexdigest()
        self.assertIn(f'oid sha256:{digest}', pointer)
        remote_object = self.remote/'lfs/objects'/digest[:2]/digest[2:4]/digest
        self.assertEqual(remote_object.read_bytes(), self.payload)
        git(self.remote, 'merge-base', '--is-ancestor', self.original_remote, result.mirror_head)
        self.assertEqual(self.publish(), result)
        # Appending another SVN revision must also append the corresponding mirror revision.
        (self.source/'code.py').write_text('next revision\n')
        self.commit(3)
        next_result = self.publish()
        git(self.remote, 'merge-base', '--is-ancestor', result.mirror_head, next_result.mirror_head)
        self.assertEqual(git(self.remote, 'show', 'master:code.py'), 'next revision')

    def test_deleted_large_blob_is_also_removed_from_reachable_git_history(self):
        (self.source/'fixture.stl').unlink()
        self.commit(3)
        self.publish()
        self.assertEqual(oversized_blobs(self.remote, 'master', 1024), [])
        self.assertIn('version https://git-lfs.github.com/spec/v1', git(self.remote, 'show', 'master^:fixture.stl'))

    def test_divergent_remote_is_not_overwritten(self):
        self.publish()
        # An independent remote-only commit must stop the next publication.
        tip = git(self.remote, 'rev-parse', 'master')
        tree = git(self.remote, 'rev-parse', 'master^{tree}')
        git(self.remote, 'config', 'user.name', 'Other Contributor')
        git(self.remote, 'config', 'user.email', 'other@example.invalid')
        other = git(self.remote, 'commit-tree', tree, '-p', tip, '-m', 'Remote-only work')
        git(self.remote, 'update-ref', 'refs/heads/master', other)
        with self.assertRaisesRegex(MirrorError, 'no force-push was attempted'):
            self.publish()
        self.assertEqual(git(self.remote, 'rev-parse', 'master'), other)

    def test_unpublished_source_commit_is_rejected_before_upload(self):
        (self.source/'code.py').write_text('not in svn\n')
        git(self.source, 'add', 'code.py')
        git(self.source, 'commit', '-m', 'Unpublished')
        with self.assertRaisesRegex(MirrorError, 'Publish to SVN first'):
            self.publish()
        self.assertEqual(git(self.remote, 'rev-parse', 'master'), self.original_remote)


if __name__ == '__main__':
    unittest.main()
