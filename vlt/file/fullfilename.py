import os
import shutil

def fullfilename(filename: str, usewhich: bool = True) -> str:
    """
    Return the full path file name of a file.

    Given either a full file name (with path) or just a filename
    (without path), returns the full path filename FULLNAME.

    If FILENAME does not exist in the present working directory,
    but is on the Python path (or current dir), it is located using
    shutil.which (for executables) or just checks existence?

    The MATLAB function uses `which` which searches MATLAB path.
    In Python, we usually don't search PATH for data files unless specified.
    But `shutil.which` searches PATH.

    Args:
        filename: The filename or path.
        usewhich: Whether to use `which` to find the file (default: True).

    Returns:
        The absolute path to the file.
    """

    # Check if we have folder name
    dirname, fname = os.path.split(filename)

    if not dirname:
        if usewhich:
            # Try to find in current directory first
            if os.path.exists(filename):
                return os.path.abspath(filename)
            # Try shutil.which (mostly for executables)
            found = shutil.which(filename)
            if found:
                return os.path.abspath(found)

        # If not found or usewhich is False
        return os.path.abspath(filename)
    else:
        # We have a folder name
        if os.path.isabs(filename):
            return filename
        else:
            return os.path.abspath(filename)
