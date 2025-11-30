import os

def mfile2package(mfilename: str) -> str:
    """
    Return the package name (if any) from a full path mfile name.

    Args:
        mfilename: The full path to the file.

    Returns:
        The package name of the m file.

    Example:
        pname = mfile2package('/Users/me/Documents/+mypackage/myf.m')
        # pname = 'mypackage.myf'
    """

    # drop the extension
    base_path, _ = os.path.splitext(mfilename)

    # In Python, we don't usually use '+' for packages.
    # But this function is seemingly used to generate documentation/names from file paths
    # that might still follow the MATLAB convention or simply to extract package structure.
    # The MATLAB implementation looks for '+' in the path.

    # If this is for parsing MATLAB files on disk, we should respect the '+' convention if present.
    # However, if this is for Python files, we might need to adjust.
    # Given the context (matlab2markdown), it is processing MATLAB files.

    # Find the first '+'
    try:
        first_plus_index = base_path.index('+')
    except ValueError:
        # If no +, return just the filename without path and extension
        return os.path.basename(base_path)

    # Extract from the first + onwards
    pname = base_path[first_plus_index+1:]

    # Replace '/+' (or '\+') with '.'
    # The MATLAB code does: strrep(pname, [filesep '+'], '.')
    pname = pname.replace(os.path.sep + '+', '.')

    # The MATLAB code also does:
    # fsep = find(pname==filesep);
    # pname(fsep(end))='.';
    # It seems it expects the last separator to be part of the package structure (separating package from file)

    # Let's replicate this behavior.
    # At this point, pname might look like "mypackage/myf" (if we started with +mypackage/myf)
    # or "pkg1.pkg2/myf" (if we had +pkg1/+pkg2/myf) due to the replacement above.

    # We want to replace the LAST file separator with '.'
    # Note: os.path.sep is system dependent.

    last_sep_index = pname.rfind(os.path.sep)
    if last_sep_index != -1:
        pname = pname[:last_sep_index] + '.' + pname[last_sep_index+1:]

    return pname
