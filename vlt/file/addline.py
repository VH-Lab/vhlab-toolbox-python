import os
import time

# Note: This is a simplified version of addline without file locking for now,
# as the full locking mechanism in MATLAB (checkout_lock_file) is complex to port
# and requires additional files. Python's file appending is atomic for small writes on POSIX,
# but not strictly guaranteed across all systems/sizes.
# Given the user request scope, implementing locking might be overkill unless required.
# But vlt.app.log relies on it.

def addline(filename: str, message: str) -> tuple[bool, str]:
    """
    Add a line of text to a text file.

    Args:
        filename: The path to the file.
        message: The message to append.

    Returns:
        (b, errormsg): b is True if successful, errormsg describes error if any.
    """

    try:
        # Create directories if needed (touch does this)
        # But here we should do it explicitly if file doesn't exist

        fullname = os.path.abspath(filename)
        parent_dir = os.path.dirname(fullname)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        with open(fullname, 'a', encoding='utf-8') as f:
            f.write(message + '\n')

        return True, ""
    except Exception as e:
        return False, str(e)
