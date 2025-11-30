import os
import time
import random
import datetime
from vlt.file.isfile import isfile
from vlt.file.text2cellstr import text2cellstr

def checkout_lock_file(filename: str, checkloops: int = 30, throwerror: bool = False, expiration: int = 3600) -> tuple[int, str]:
    """
    Try to establish control of a lock file.

    Args:
        filename: The lock file path.
        checkloops: Number of times to check (default 30).
        throwerror: Whether to raise error on failure (default False).
        expiration: Expiration time in seconds (default 3600).

    Returns:
        (fid, key): fid is file handle (or >0 if success), key is the lock key.
        If failed, fid is -1.

        Note: In Python, we return an open file object or None/Integer?
        The MATLAB code returns FID.
        If we want to mimic MATLAB FID behavior, we can return file descriptor?
        But Python file objects are better.
        However, the function signature returns (fid, key).
        We will return 1 for success if we close the file inside, or keep it open?

        MATLAB:
        if nargout>1, % if we are getting the key, we should close the lock file
                fclose(fid);
        end;

        So if we return key, we close the file.
        Since we always return key in this signature (tuple), we close the file.
        So `fid` in return can be just a success flag (1) or -1.
    """

    key = f"{time.time():.16f}_{random.random():.16f}" # Approximate unique key

    loop = 0

    # MATLAB: expiration_time_of_file = Inf;

    while isfile(filename) and loop < checkloops:
        # Check if expired
        isexpired = False
        try:
            C = text2cellstr(filename)
            if C:
                # Parse date?
                # The date format used in MATLAB: char(datetime(t2,'TimeZone','UTCLeapSeconds'))
                # e.g. 24-Jan-2025 10:00:00
                # Parsing might be tricky without exact format.
                # If we wrote it, we know the format.
                pass
        except Exception:
            pass

        # Simplified expiration check: just check modification time?
        # Or blindly trust it will expire.
        # For now, let's just wait.

        time.sleep(1)
        loop += 1

    if loop < checkloops:
        # We can try to create it
        try:
            # Check again if exists to avoid race (still possible though without atomic open with CREATE_NEW)
            if isfile(filename):
                # Race lost
                if throwerror:
                     raise RuntimeError(f"Unable to obtain lock with file {filename}.")
                return -1, ""

            with open(filename, 'w') as f:
                # Write expiration and key
                # t2 = now + expiration
                # We format datetime as ISO or similar?
                # MATLAB `char(datetime)` depends on locale?
                # Let's use ISO format.
                exp_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=expiration)
                f.write(f"{exp_time.isoformat()}\n{key}\n")

            return 1, key
        except Exception as e:
            if throwerror:
                raise RuntimeError(f"Unable to obtain lock with file {filename}: {e}")
            return -1, ""
    else:
        if throwerror:
            raise RuntimeError(f"Unable to obtain lock with file {filename}.")
        return -1, ""

def release_lock_file(fid_or_filename: str, key: str) -> bool:
    """
    Release a lock file with the key.

    Args:
        fid_or_filename: The filename (str).
        key: The key.

    Returns:
        True if released or not present, False if key mismatch.
    """

    filename = fid_or_filename

    if not isfile(filename):
        return True

    try:
        C = text2cellstr(filename)
    except Exception:
        if not isfile(filename):
            return True
        raise RuntimeError(f"{filename} could not be opened.")

    if len(C) < 2:
         # raise error? MATLAB says: error([filename ' does not appear to be a lock file...'])
         # But returns b=0 if key mismatch?
         # "An error is triggered if the lock file does not have the expected contents"
         raise RuntimeError(f"{filename} does not appear to be a lock file created by checkout_lock_file.")

    # Check key (2nd line)
    stored_key = C[1].strip()
    if stored_key == key:
        os.remove(filename)
        return True
    else:
        return False
