import os
import time
import datetime
import random
import numpy as np

# --- Basics ---

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

def cellstr2text(filename, cs):
    """
    Write a list of strings to a text file.

    vlt.file.cellstr2text(filename, cs)

    Writes the list of strings cs to the new text file filename.
    One entry is written per line.
    """
    try:
        with open(filename, 'w') as f:
            for s in cs:
                f.write(str(s) + '\n')
    except Exception as e:
        raise Exception(f"Could not open {filename} for writing: {e}")

def filename_value(filename_or_fileobj):
    """
    Return the string of a filename whether it is a filename or inside a fileobj.

    filename = vlt.file.filename_value(filename_or_fileobj)

    Given a value which may be a filename or a vlt.file.fileobj object (or similar),
    return either the filename or the fullpathfilename field of the object.
    """
    # Check if it has 'fullpathfilename' attribute
    if hasattr(filename_or_fileobj, 'fullpathfilename'):
        return str(filename_or_fileobj.fullpathfilename)
    elif hasattr(filename_or_fileobj, 'name') and hasattr(filename_or_fileobj, 'read'): # File-like object
        return str(filename_or_fileobj.name)
    else:
        return str(filename_or_fileobj)

# --- Lock ---

def checkout_lock_file(filename, checkloops=30, throwerror=False, expiration=3600):
    """
    Try to establish control of a lock file.
    Returns (fid, key). fid is 1 on success, -1 on failure.
    """
    loops = checkloops
    key = f"{datetime.datetime.now().timestamp()}_{random.random()}"

    loop = 0
    expiration_time_of_file = None

    while isfile(filename) and loop < loops:
        file_exists = isfile(filename)

        if file_exists:
            try:
                lines = text2cellstr(filename)
                if lines:
                    exp_str = lines[0].strip()
                    try:
                        expiration_time_of_file = datetime.datetime.fromisoformat(exp_str)
                    except ValueError:
                        pass # Format error
            except:
                pass # Gone or unreadable

        isexpired = False
        if expiration_time_of_file:
            if datetime.datetime.now() > expiration_time_of_file:
                isexpired = True

        if not isexpired:
            time.sleep(1)
        else:
            try:
                os.remove(filename)
            except:
                pass
        loop += 1

    if loop < loops:
        try:
            with open(filename, 'w') as f:
                t2 = datetime.datetime.now() + datetime.timedelta(seconds=expiration)
                f.write(t2.isoformat() + '\n')
                f.write(key + '\n')
            return 1, key
        except Exception as e:
            if throwerror:
                raise e
            return -1, ''
    else:
        if throwerror:
            raise Exception(f"Unable to obtain lock with file {filename}")
        return -1, ''

def release_lock_file(fid_or_filename, key):
    """
    Release a lock file given its filename and key.
    """
    filename = fid_or_filename

    if not isfile(filename):
        return True

    try:
        lines = text2cellstr(filename)
    except:
        if not isfile(filename):
            return True
        else:
            raise Exception(f"{filename} could not be opened")

    if len(lines) != 2:
         # In MATLAB it raises error.
         # "error([filename ' does not appear to be a lock file created by vlt.file.checkout_lock_file.']);"
         # We will be lenient or raise? Let's raise to match.
         raise Exception(f"{filename} does not appear to be a lock file created by vlt.file.checkout_lock_file.")

    if lines[1].strip() == key:
        os.remove(filename)
        return True
    else:
        return False

# --- Text ---

def addline(filename, message):
    """
    Add a line of text to a text file.
    Returns (b, errormsg).
    """
    fullname = fullfilename(filename)
    b, err = createpath(fullname)
    if not b:
        return False, err

    mylockfile = fullname + '-lock'
    lockfid, key = checkout_lock_file(mylockfile)

    if lockfid > 0:
        try:
            with open(fullname, 'a') as f:
                f.write(message + '\n')
            b = True
            errormsg = ''
        except Exception as e:
            b = False
            errormsg = str(e)

        release_lock_file(mylockfile, key)
    else:
        b = False
        errormsg = f"Never got control of {mylockfile}; it was busy."

    return b, errormsg
