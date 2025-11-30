import os
from vlt.file.fullfilename import fullfilename

def createpath(filename: str) -> tuple[bool, str]:
    """
    Create a directory path to a given file name, if necessary.

    Args:
        filename: The file path.

    Returns:
        (b, errormsg): b is True if successful (1 in MATLAB), errormsg is empty if success.
        Note: MATLAB implementation returns b=1 for success, 0 for failure.
    """

    try:
        fullname = fullfilename(filename)
        dirname = os.path.dirname(fullname)

        if not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)

        return True, ""
    except Exception as e:
        return False, str(e)
