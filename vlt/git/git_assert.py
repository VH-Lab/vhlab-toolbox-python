import shutil

def git_assert():
    """
    Check if git is installed/available.

    Returns:
        bool: True if git is found, False otherwise.
    """
    return shutil.which('git') is not None
