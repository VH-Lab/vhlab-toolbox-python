import subprocess
import os
from vlt.git.git_assert import git_assert

def git_repo_version(filepath):
    """
    Return commit number and remote location of repository.

    Args:
        filepath (str): Path to the repository or a file inside it.

    Returns:
        tuple: (v, remote) where v is the commit hash and remote is the origin URL.

    Raises:
        RuntimeError: If git is not found or if the git command fails.
    """
    if not git_assert():
        raise RuntimeError('Could not locate git on this machine.')

    # Handle if filepath is a file or directory
    cwd = filepath
    if os.path.isfile(filepath):
        cwd = os.path.dirname(filepath)

    try:
        # Get commit hash
        # git -C <path> runs git as if started in <path>
        result_v = subprocess.run(
            ['git', '-C', cwd, 'rev-parse', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        v = result_v.stdout.strip()

        # Get remote origin url
        result_r = subprocess.run(
            ['git', '-C', cwd, 'config', '--get', 'remote.origin.url'],
            capture_output=True,
            text=True,
            check=True
        )
        remote = result_r.stdout.strip()

        return v, remote

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f'Error getting git info for path {filepath}.') from e
