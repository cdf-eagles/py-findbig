"""Tests for the release scripts in scripts/, run with python3 -m unittest."""

import os
import shutil
import subprocess
import tempfile
import unittest

import findbig

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEXT_VERSION = os.path.join(ROOT, "scripts", "next-version.sh")
CHECK_VERSION = os.path.join(ROOT, "scripts", "check-release-version.sh")

# A git that ignores the user's own configuration (signing, hooks, editor).
GIT_ENV = dict(
    os.environ,
    GIT_CONFIG_GLOBAL=os.devnull,
    GIT_CONFIG_NOSYSTEM="1",
    GIT_AUTHOR_NAME="Test",
    GIT_AUTHOR_EMAIL="test@example.invalid",
    GIT_COMMITTER_NAME="Test",
    GIT_COMMITTER_EMAIL="test@example.invalid",
)


def run(args, cwd=None):
    """Run args; return the exit code, stdout, and stderr."""
    done = subprocess.run(
        args,
        cwd=cwd,
        env=GIT_ENV,
        capture_output=True,
        text=True,
        check=False,
    )
    return done.returncode, done.stdout, done.stderr


@unittest.skipIf(shutil.which("git") is None, "git is not installed")
class TestNextVersion(unittest.TestCase):
    """scripts/next-version.sh proposes the bump from branch prefixes."""

    def setUp(self):
        self.repo = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.repo)
        self.git("init", "--quiet", "--initial-branch=main")
        self.commit("Initial commit")
        self.number = 0

    def git(self, *args):
        """Run git in the test repository and fail on an error."""
        code, out, err = run(["git", *args], cwd=self.repo)
        self.assertEqual(code, 0, err)
        return out

    def commit(self, subject):
        """Add an empty commit with subject."""
        self.git("commit", "--quiet", "--allow-empty", "-m", subject)

    def merge(self, branch):
        """Add a commit read as a pull request merged from branch."""
        self.number += 1
        self.commit(f"Merge pull request #{self.number} from owner/{branch}")

    def propose(self):
        """Run next-version.sh on main; return its exit code and output."""
        code, out, err = run(["sh", NEXT_VERSION, "main"], cwd=self.repo)
        return code, out + err

    def test_feat_bumps_the_minor_version(self):
        """A feat/ branch since v0.3.0 proposes v0.4.0 and its rc.1."""
        self.git("tag", "v0.3.0")
        self.merge("feat/release-process")
        code, out = self.propose()
        self.assertEqual(code, 0, out)
        self.assertIn("Next version:     v0.4.0", out)
        self.assertIn("git tag -s v0.4.0-rc.1 -m v0.4.0-rc.1", out)

    def test_fix_bumps_the_patch_version(self):
        """Only fix/ branches propose a patch release."""
        self.git("tag", "v0.3.0")
        self.merge("fix/one")
        self.merge("build/tools")
        code, out = self.propose()
        self.assertEqual(code, 0, out)
        self.assertIn("Next version:     v0.3.1", out)

    def test_major_outranks_feat(self):
        """A major/ branch wins over feat/ and fix/."""
        self.git("tag", "v0.3.0")
        self.merge("fix/one")
        self.merge("major/break")
        self.merge("feat/more")
        code, out = self.propose()
        self.assertEqual(code, 0, out)
        self.assertIn("Next version:     v1.0.0", out)

    def test_other_branches_release_nothing(self):
        """build/, ignore/, and unknown prefixes give exit status 1."""
        self.git("tag", "v0.3.0")
        for branch in ("build/tools", "ignore/notes", "feature/old-name"):
            self.merge(branch)
        code, out = self.propose()
        self.assertEqual(code, 1, out)
        self.assertIn("no fix/, feat/, or major/ pull request", out)

    def test_next_release_candidate_number(self):
        """An existing v0.4.0-rc.1 makes the next candidate rc.2."""
        self.git("tag", "v0.3.0")
        self.merge("feat/release-process")
        self.git("tag", "v0.4.0-rc.1")
        code, out = self.propose()
        self.assertEqual(code, 0, out)
        self.assertIn("git tag -s v0.4.0-rc.2 -m v0.4.0-rc.2", out)

    def test_unknown_ref_is_a_usage_error(self):
        """A ref that does not exist gives exit status 2."""
        code, _, err = run(["sh", NEXT_VERSION, "nowhere"], cwd=self.repo)
        self.assertEqual(code, 2)
        self.assertIn("unknown ref", err)


class TestCheckReleaseVersion(unittest.TestCase):
    """scripts/check-release-version.sh compares a tag with findbig.py."""

    def setUp(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        self.script = os.path.join(tmp, "findbig.py")
        with open(self.script, "w", encoding="utf-8") as handle:
            handle.write('import os\n\n__version__ = "1.2.3"\n')

    def check(self, tag, path=None):
        """Run the check; return its exit code and output."""
        code, out, err = run(["sh", CHECK_VERSION, tag, path or self.script])
        return code, out + err

    def test_final_and_candidate_tags_match(self):
        """vX.Y.Z and vX.Y.Z-rc.N both match __version__ X.Y.Z."""
        for tag in ("v1.2.3", "v1.2.3-rc.1", "v1.2.3-rc.12"):
            code, out = self.check(tag)
            self.assertEqual(code, 0, out)

    def test_another_version_is_refused(self):
        """A tag naming another version gives exit status 1."""
        for tag in ("v1.2.4", "v1.2.4-rc.1", "v1.2.30"):
            code, out = self.check(tag)
            self.assertEqual(code, 1, out)
            self.assertIn("has __version__ 1.2.3", out)

    def test_unsupported_tags_are_usage_errors(self):
        """Tags outside vX.Y.Z and vX.Y.Z-rc.N give exit status 2."""
        for tag in ("1.2.3", "v1.2.3-beta", "v1.2.3-rc.x", "latest"):
            code, out = self.check(tag)
            self.assertEqual(code, 2, out)
            self.assertIn(f"unsupported tag {tag}", out)

    def test_file_without_a_version_is_a_usage_error(self):
        """A file with no __version__ line gives exit status 2."""
        with open(self.script, "w", encoding="utf-8") as handle:
            handle.write("import os\n")
        code, out = self.check("v1.2.3")
        self.assertEqual(code, 2, out)
        self.assertIn("expected one __version__ line", out)

    def test_repository_script_matches_its_own_version(self):
        """The check reads findbig.py's real __version__ line."""
        path = os.path.join(ROOT, "findbig.py")
        code, out = self.check(f"v{findbig.__version__}", path)
        self.assertEqual(code, 0, out)


if __name__ == "__main__":
    unittest.main()
