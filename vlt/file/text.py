import os
from .basics import createpath, fullfilename
from .lock import checkout_lock_file, release_lock_file

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
