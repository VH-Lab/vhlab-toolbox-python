import os
import pathlib

def touch(filename: str):
    """
    Create a file (empty) if it does not already exist.

    This function checks to see if FILENAME exists. If it does not
    exist, it creates a blank file and creates all necessary
    directories that may be required.

    If the file does not exist and cannot be created, an error is
    generated.
    """

    # Check if exists
    if os.path.exists(filename):
        return

    # Get absolute path
    fullname = os.path.abspath(filename)

    # Create path
    parent_dir = os.path.dirname(fullname)
    if not os.path.exists(parent_dir):
        try:
            os.makedirs(parent_dir, exist_ok=True)
        except OSError as e:
            raise IOError(f"Could not create path {parent_dir}: {e}")

    # Create empty file
    try:
        with open(fullname, 'w') as f:
            pass
    except IOError as e:
        raise IOError(f"Could not open file {fullname}: {e}")
