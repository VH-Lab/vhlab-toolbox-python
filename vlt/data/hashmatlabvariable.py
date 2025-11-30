import hashlib
import pickle
import zlib

def hashmatlabvariable(d, algorithm='DataHash/MD5'):
    """
    Creates a hashed value based on the binary data in the variable D.

    Parameters
    ----------
    d : any
        The variable to hash.
    algorithm : str, optional
        Algorithm to be used. Default is 'DataHash/MD5'.
        Options:
            'DataHash/MD5': Returns an MD5 hexdigest.
            'pm_hash/crc': Returns a 32-bit CRC.

    Returns
    -------
    h : str or int
        The hash value.
    """

    if algorithm.lower() == 'datahash/md5':
        try:
            # We use pickle to get bytes from the object.
            # Note: This will not produce the same hash as Matlab.
            # It provides consistency within the Python environment.
            data_bytes = pickle.dumps(d)
            h = hashlib.md5(data_bytes).hexdigest()
        except Exception as e:
            raise e
    elif algorithm.lower() == 'pm_hash/crc':
        data_bytes = pickle.dumps(d)
        h = zlib.crc32(data_bytes) & 0xFFFFFFFF
    else:
        raise ValueError(f"Unknown algorithm {algorithm}.")

    return h
