import os

def fixpath(pathstr):
    """
    FIXPATH - Ensures a path string ends with a file separator

    PATHN = vlt.file.fixpath(PATHSTR)

    Checks the string PATHSTR to see if it ends in os.sep.
    PATHN is simply PATHSTR with os.sep attached at the end if necessary.
    """
    if not pathstr:
        return pathstr
    if not pathstr.endswith(os.sep):
        return pathstr + os.sep
    return pathstr
