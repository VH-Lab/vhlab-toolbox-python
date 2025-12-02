import os

def fixtilde(filename):
    """
    FIXTILDE - Removes ~ from filenames and replaces with user home directory

    NEWNAME = vlt.file.fixtilde(FILENAME)

    Removes '~' symbol for a user's home directory and replaces it with the actual path.
    """
    if not filename:
        return filename
    return os.path.expanduser(filename)
