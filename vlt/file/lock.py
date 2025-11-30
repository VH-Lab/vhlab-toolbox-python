import os
import time
import datetime
import random
from .basics import isfile, text2cellstr

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
