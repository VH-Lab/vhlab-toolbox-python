import os

def findfunctionusedir(dirname, minfo, **kwargs):
    """
    Determine where a function is called in a directory of m-files.

    Args:
        dirname (str): Directory to search.
        minfo (dict or list): Info of function(s) to search for.
        **kwargs:
            IgnorePackages (int/bool): Default False.
            IgnoreClassDirs (int/bool): Default False.

    Returns:
        list of dicts: List of usage structures.
    """
    from .findfunctionusefile import findfunctionusefile

    IgnorePackages = kwargs.get('IgnorePackages', 0)
    IgnoreClassDirs = kwargs.get('IgnoreClassDirs', 0)

    fuse = []

    # Handle list of minfo
    if isinstance(minfo, list):
        for m in minfo:
            fuse.extend(findfunctionusedir(dirname, m, **kwargs))
        return fuse

    if not os.path.isdir(dirname):
        return fuse

    try:
        d = os.listdir(dirname)
    except OSError:
        return fuse

    d.sort()

    for name in d:
        if name in ['.', '..']:
            continue

        full_path = os.path.join(dirname, name)

        if os.path.isdir(full_path):
            if IgnorePackages and name.startswith('+'):
                continue
            if IgnoreClassDirs and name.startswith('@'):
                continue

            fuse.extend(findfunctionusedir(full_path, minfo, **kwargs))
        else:
            _, ext = os.path.splitext(name)
            if ext == '.m':
                fuse.extend(findfunctionusefile(full_path, minfo))

    return fuse
