import unittest
import os
import shutil
import subprocess
from vlt.git.git_assert import git_assert
from vlt.git.git_repo_version import git_repo_version

class TestGit(unittest.TestCase):
    def test_git_assert(self):
        # Assuming git is installed in the environment
        self.assertTrue(git_assert())

    def test_git_repo_version(self):
        # We can test this on the current repo
        # Use the current directory
        cwd = os.getcwd()

        # This assumes we are in a git repo. The sandbox is a git repo.
        try:
            v, remote = git_repo_version(cwd)
            self.assertIsInstance(v, str)
            self.assertIsInstance(remote, str)
            self.assertGreater(len(v), 0)
            # remote might be empty if no remote is configured, but usually there is one in the sandbox?
            # Actually sandbox might not have remote origin configured if it's a fresh clone or similar.
            # But git_repo_version raises error if command fails.
            # If `git config --get remote.origin.url` returns nothing (and exit 0? or 1?), we should check.
            # git config returns exit code 1 if the key is not found.

            # Let's check if we expect a remote.
            # If no remote, git_repo_version raises RuntimeError.
            # So if this test passes, we found a remote.
            # If it fails, we might need to mock or skip if no remote.
        except RuntimeError:
            # Maybe not a git repo or no remote?
            # We can try to init a temp git repo
            self.skipTest("Current directory might not be a git repo with remote origin")

    def test_git_repo_version_temp_repo(self):
        # Create a temp dir, init git, check version
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            subprocess.run(['git', 'init'], cwd=tmpdir, check=True)
            # Commit something so HEAD exists
            subprocess.run(['git', 'config', 'user.email', 'you@example.com'], cwd=tmpdir, check=True)
            subprocess.run(['git', 'config', 'user.name', 'Your Name'], cwd=tmpdir, check=True)
            with open(os.path.join(tmpdir, 'test.txt'), 'w') as f:
                f.write('test')
            subprocess.run(['git', 'add', 'test.txt'], cwd=tmpdir, check=True)
            subprocess.run(['git', 'commit', '-m', 'initial'], cwd=tmpdir, check=True)

            # Add a remote
            subprocess.run(['git', 'remote', 'add', 'origin', 'https://example.com/repo.git'], cwd=tmpdir, check=True)

            v, remote = git_repo_version(tmpdir)
            self.assertEqual(len(v), 40) # sha1
            self.assertEqual(remote, 'https://example.com/repo.git')

            # Test with a file inside
            v2, remote2 = git_repo_version(os.path.join(tmpdir, 'test.txt'))
            self.assertEqual(v, v2)
            self.assertEqual(remote, remote2)

if __name__ == '__main__':
    unittest.main()
