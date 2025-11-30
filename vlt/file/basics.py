import os

def isfilepathroot(filepath):
    """
    Determines if a FILEPATH is at the root of a drive or not.
    """
    if os.name == 'nt': # Windows
        return ':' in filepath or filepath.startswith('/') or filepath.startswith('\\')
    else: # Unix
        return filepath.startswith('/')

def isfile(filename):
    """
    Checks if a file exists.
    """
    return os.path.isfile(filename)

def fullfilename(filename, usewhich=True):
    """
    Returns the full path file name of a file.
    """
    if os.path.isabs(filename):
        return filename
    return os.path.abspath(filename)

def createpath(filename):
    """
    Create a directory path to a given file name, if necessary.
    Returns (b, errormsg).
    """
    try:
        dirname = os.path.dirname(filename)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)
        return True, ''
    except Exception as e:
        return False, str(e)

def touch(filename):
    """
    Create a file (empty) if it does not already exist.
    """
    if os.path.exists(filename):
        return

    fullname = fullfilename(filename)
    b, err = createpath(fullname)
    if not b:
        raise Exception(err)

    try:
        with open(fullname, 'w') as f:
            pass
    except Exception as e:
        raise Exception(f"Could not open file {fullname}: {e}")

def text2cellstr(filename):
    """
    Read a list of strings from a text file.
    """
    if not os.path.exists(filename):
        raise Exception(f"Could not open file {filename} for reading.")

    with open(filename, 'r') as f:
        lines = f.read().splitlines()
    return lines
