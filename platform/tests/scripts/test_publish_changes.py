"""Exercise publication against disposable Git repos; SVN and push are simulated."""
import contextlib
import io
from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts.publish_changes import Git, PublicationError, parse_args, publish


class SimulatedPublicationGit(Git):
    def __init__(self, root):
        super().__init__(root)
        self.commands = []
        self.fail_svn = False
        self.fail_push = False
        self.fail_remote = None
        self.rewrite_svn = True

    def read(self, *args, **kwargs):
        if args == ("svn", "--version"):
            return "git-svn test adapter"
        return super().read(*args, **kwargs)

    def run(self, *args):
        self.commands.append(args)
        if args == ("svn", "dcommit"):
            if self.fail_svn:
                raise PublicationError("simulated SVN failure")
            if self.rewrite_svn:
                message = self.read("log", "-1", "--format=%B")
                if "git-svn-id:" not in message:
                    self.local("commit", "--amend", "-m", message + "\n\ngit-svn-id: https://example.invalid/svn/trunk@2 test-uuid")
                self.local("update-ref", "refs/remotes/git-svn", self.read("rev-parse", "HEAD"))
            return
        if args[0] == "push":
            if self.fail_push or args[1] == self.fail_remote:
                raise PublicationError("simulated push authentication failure")
            return
        self.local(*args)

    def publish_remote(self, remote):
        # Mirror integration (including real LFS migration) is exercised separately.
        self.run("push", remote, "master")

    def local(self, *args):
        subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True, text=True)


class PublishChangesTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.git = SimulatedPublicationGit(self.root)
        self.git.local("init", "-b", "master")
        self.git.local("config", "user.name", "Publication Test")
        self.git.local("config", "user.email", "test@example.invalid")
        self.git.local("config", "commit.gpgsign", "false")
        self.git.local("config", "core.hooksPath", str(self.root / "unused-hooks"))
        self.git.local("config", "svn-remote.svn.url", "https://example.invalid/svn/trunk")
        self.git.local("remote", "add", "github-svn-mirror", "https://example.invalid/repo.git")
        self.git.local("remote", "add", "secondary-test", "https://example.invalid/gitlab.git")
        (self.root / "a.txt").write_text("original\n")
        self.git.local("add", "a.txt")
        self.git.local("commit", "-m", "Initial\n\ngit-svn-id: https://example.invalid/svn/trunk@1 test-uuid")
        self.git.local("update-ref", "refs/remotes/git-svn", self.git.read("rev-parse", "HEAD"))

    def execute(self, argv, paths=None):
        with contextlib.redirect_stdout(io.StringIO()):
            publish(self.git, parse_args([*argv, "--remote", "github-svn-mirror", "--remote", "secondary-test"] if "--remote" not in argv else argv), paths or [])

    def test_all_commits_then_svn_then_pushes_rewritten_head(self):
        (self.root / "a.txt").write_text("edited\n")
        (self.root / "new.txt").write_text("new\n")
        self.execute(["--all", "-m", "Update files"])
        self.assertEqual(self.git.commands[-3:], [("svn", "dcommit"), ("push", "github-svn-mirror", "master"), ("push", "secondary-test", "master")])
        self.assertEqual(self.git.read("status", "--porcelain"), "")
        self.assertEqual(self.git.read("rev-parse", "HEAD"), self.git.read("rev-parse", "refs/remotes/git-svn"))
        self.assertIn("git-svn-id:", self.git.read("log", "-1", "--format=%B"))

    def test_dry_run_does_not_change_index_head_or_files(self):
        (self.root / "a.txt").write_text("edited\n")
        before = self.git.read("rev-parse", "HEAD")
        self.execute(["--all", "-m", "Preview", "--dry-run"])
        self.assertEqual(self.git.commands, [])
        self.assertEqual(self.git.read("rev-parse", "HEAD"), before)
        self.assertEqual(self.git.read("diff", "--cached", "--name-only"), "")
        self.assertEqual((self.root / "a.txt").read_text(), "edited\n")

    def test_svn_failure_never_pushes_and_keeps_local_commit(self):
        (self.root / "a.txt").write_text("edited\n")
        self.git.fail_svn = True
        with self.assertRaisesRegex(PublicationError, "SVN failure"):
            self.execute(["--all", "-m", "Keep my commit"])
        self.assertFalse(any(cmd[0] == "push" for cmd in self.git.commands))
        self.assertEqual(self.git.read("rev-list", "--count", "refs/remotes/git-svn..HEAD"), "1")

    def test_push_failure_can_resume_without_duplicate_commit(self):
        (self.root / "a.txt").write_text("edited\n")
        self.git.fail_push = True
        with self.assertRaisesRegex(PublicationError, "authentication failure"):
            self.execute(["--all", "-m", "Publish once"])
        head = self.git.read("rev-parse", "HEAD")
        self.git.fail_push = False
        self.git.commands.clear()
        self.execute(["--resume"])
        self.assertEqual(self.git.read("rev-parse", "HEAD"), head)
        self.assertEqual(self.git.commands, [("svn", "dcommit"), ("push", "github-svn-mirror", "master"), ("push", "secondary-test", "master")])

    def test_secondary_failure_can_resume_after_svn_and_gitea_succeed(self):
        (self.root / "a.txt").write_text("edited\n")
        self.git.fail_remote = "secondary-test"
        with self.assertRaisesRegex(PublicationError, "authentication failure"):
            self.execute(["--all", "-m", "Publish once"])
        head = self.git.read("rev-parse", "HEAD")
        self.assertEqual(head, self.git.read("rev-parse", "refs/remotes/git-svn"))
        self.git.fail_remote = None
        self.git.commands.clear()
        self.execute(["--resume"])
        self.assertEqual(self.git.read("rev-parse", "HEAD"), head)
        self.assertEqual(self.git.commands, [("svn", "dcommit"), ("push", "github-svn-mirror", "master"), ("push", "secondary-test", "master")])

    def test_missing_secondary_remote_stops_before_commit_or_svn(self):
        self.git.local("remote", "remove", "secondary-test")
        (self.root / "a.txt").write_text("edited\n")
        with self.assertRaises(PublicationError):
            self.execute(["--all", "-m", "Missing remote"])
        self.assertEqual(self.git.commands, [])

    def test_default_destination_is_only_github(self):
        self.assertEqual(parse_args(["--resume"]).remote, ["github-svn-mirror"])
        with contextlib.redirect_stdout(io.StringIO()):
            publish(self.git, parse_args(["--resume"]), [])
        self.assertEqual(self.git.commands, [("svn", "dcommit"), ("push", "github-svn-mirror", "master")])

    def test_explicit_remote_overrides_defaults(self):
        self.execute(["--resume", "--remote", "github-svn-mirror"])
        self.assertEqual(self.git.commands, [("svn", "dcommit"), ("push", "github-svn-mirror", "master")])

    def test_dry_run_lists_both_pushes_after_svn(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            publish(self.git, parse_args(["--resume", "--dry-run", "--remote", "github-svn-mirror", "--remote", "secondary-test"]), [])
        plan = output.getvalue()
        self.assertLess(plan.index("git svn dcommit"), plan.index("GitHub LFS projection:"))
        self.assertLess(plan.index("GitHub LFS projection:"), plan.index("git push secondary-test master"))
        self.assertEqual(self.git.commands, [])

    def test_github_only_allows_unrelated_edits_without_committing_or_touching_svn(self):
        (self.root / "a.txt").write_text("unrelated edit\n")
        before = self.git.read("rev-parse", "HEAD")
        with contextlib.redirect_stdout(io.StringIO()):
            publish(self.git, parse_args(["--resume", "--github-only"]), [])
        self.assertEqual(self.git.commands, [("push", "github-svn-mirror", "master")])
        self.assertEqual(self.git.read("rev-parse", "HEAD"), before)
        self.assertEqual((self.root / "a.txt").read_text(), "unrelated edit\n")

    def test_github_only_refuses_a_commit_not_yet_published_to_svn(self):
        (self.root / "a.txt").write_text("new commit\n")
        self.git.local("add", "a.txt")
        self.git.local("commit", "-m", "Not in SVN")
        with self.assertRaisesRegex(PublicationError, "remain unpublished"):
            with contextlib.redirect_stdout(io.StringIO()):
                publish(self.git, parse_args(["--resume", "--github-only"]), [])
        self.assertEqual(self.git.commands, [])

    def test_unsynced_head_is_not_pushed_even_if_svn_returns_success(self):
        (self.root / "a.txt").write_text("edited\n")
        self.git.rewrite_svn = False
        with self.assertRaisesRegex(PublicationError, "remain unpublished"):
            self.execute(["--all", "-m", "Unsynced"])
        self.assertFalse(any(cmd[0] == "push" for cmd in self.git.commands))

    def test_staged_only_rejects_unrelated_untracked_files_before_commit(self):
        (self.root / "a.txt").write_text("edited\n")
        self.git.local("add", "a.txt")
        (self.root / "unrelated.txt").write_text("preserve\n")
        with self.assertRaisesRegex(PublicationError, "Unstaged/untracked"):
            self.execute(["-m", "Selected"])
        self.assertEqual(self.git.commands, [])
        self.assertEqual((self.root / "unrelated.txt").read_text(), "preserve\n")

    def test_partial_paths_reject_leftovers_before_commit(self):
        (self.root / "a.txt").write_text("edited\n")
        (self.root / "unrelated.txt").write_text("preserve\n")
        with self.assertRaisesRegex(PublicationError, "no commit was created"):
            self.execute(["-m", "Selected", "a.txt"], ["a.txt"])
        self.assertEqual(self.git.commands, [("add", "--", "a.txt")])
        self.assertEqual(self.git.read("rev-list", "--count", "refs/remotes/git-svn..HEAD"), "0")

    def test_protected_branch_is_rejected_before_mutation(self):
        self.git.local("checkout", "-b", "run_main.py")
        with self.assertRaisesRegex(PublicationError, "master work branch"):
            self.execute(["--resume"])
        self.assertEqual(self.git.commands, [])

    def test_empty_staging_does_not_create_commit(self):
        with self.assertRaisesRegex(PublicationError, "Nothing staged"):
            self.execute(["-m", "Empty"])
        self.assertEqual(self.git.commands, [])

    def test_whitespace_error_prevents_commit_and_publication(self):
        (self.root / "a.txt").write_text("bad trailing space \n")
        with self.assertRaises(subprocess.CalledProcessError):
            self.execute(["--all", "-m", "Whitespace"])
        self.assertFalse(any(cmd[0] in ("commit", "svn", "push") for cmd in self.git.commands))


if __name__ == "__main__":
    unittest.main()
