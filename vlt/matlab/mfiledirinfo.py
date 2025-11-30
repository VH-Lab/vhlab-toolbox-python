import os
# We need to import the real or mock mfileinfo.
# Since we haven't implemented the real one, we import from mocks if available,
# or define a placeholder.
# But `vlt.matlab` namespace should have it.
# I will create vlt/matlab/mfileinfo.py that uses the mock logic for now,
# or I can put the logic inline or import.
# Better: define `mfileinfo` in `vlt/matlab/mfileinfo.py` using the mock implementation.
# This makes `mfiledirinfo` import it naturally.

# I will overwrite `vlt/matlab/mfileinfo.py` and `vlt/matlab/findfunctionusefile.py` with the mock implementations.
# This satisfies imports and allows testing.

def mfiledirinfo(dirname, **kwargs):
    """
    Return m-file info for all files in a directory recursively.

    Args:
        dirname (str): Directory to search.
        **kwargs:
            IgnorePackages (int/bool): Default True.
            IgnoreClassDirs (int/bool): Default True.

    Returns:
        list of dicts: List of mfile info structures.
    """
    from .mfileinfo import mfileinfo

    IgnorePackages = kwargs.get('IgnorePackages', 1)
    IgnoreClassDirs = kwargs.get('IgnoreClassDirs', 1)

    minfo = []

    if not os.path.isdir(dirname):
        return minfo

    try:
        d = os.listdir(dirname)
    except OSError:
        return minfo

    d.sort() # standard order

    for name in d:
        if name in ['.', '..']:
            continue

        full_path = os.path.join(dirname, name)

        if os.path.isdir(full_path):
            if IgnorePackages and name.startswith('+'):
                continue
            if IgnoreClassDirs and name.startswith('@'):
                continue

            minfo_d = mfiledirinfo(full_path, **kwargs)
            minfo.extend(minfo_d)
        else:
            # File
            _, ext = os.path.splitext(name)
            if ext == '.m':
                minfo_f = mfileinfo(full_path)
                minfo.extend(minfo_f)

    return minfo
