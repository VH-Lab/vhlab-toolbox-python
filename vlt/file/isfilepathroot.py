import os

def isfilepathroot(filepath: str) -> bool:
    """
    Determine if a file path is at the root or not.

    Args:
        filepath: The file path to check.

    Returns:
        True if the path is a root path, False otherwise.
    """

    # On Windows, drive root (e.g., C:\) or UNC root (\\)
    # On Unix, /

    # Python's os.path.splitdrive might help
    drive, tail = os.path.splitdrive(filepath)

    if os.name == 'nt':
         # Windows
         # Check if it starts with a drive letter and colon and backslash/slash
         # e.g. C:\
         # or \\server\share

         # The MATLAB code checks for `$:\` or `/` at start.

         if len(filepath) >= 3 and filepath[1] == ':' and filepath[2] in ['\\', '/']:
             return True
         if filepath.startswith('/') or filepath.startswith('\\'): # Assuming root relative?
             # MATLAB code: b2 = filepath(1)=='/'; % unix file separator is valid on Windows
             # It seems it considers '/' as root too.
             return True

         return False
    else:
        # Unix
        return filepath.startswith('/')
