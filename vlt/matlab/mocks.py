# Mock implementation of mfileinfo and findfunctionusefile
# Since these are dependencies not in the list but required for the others.

def mfileinfo(filepath):
    """
    Mock mfileinfo.
    Parses a MATLAB file to get function name.

    Args:
        filepath (str): Path to .m file.

    Returns:
        list of dicts: [{'name': function_name, ...}]
    """
    import os
    if not os.path.exists(filepath):
        raise ValueError(f"File {filepath} does not exist.")

    # Simple parser: look for "function ... = name(...)"
    name = None
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('function '):
                # parsing logic
                # 1. function [y] = myfunc(x)
                # 2. function y = myfunc(x)
                # 3. function myfunc(x)
                # 4. function myfunc

                # Remove 'function '
                rest = line[9:].strip()

                if '=' in rest:
                    parts = rest.split('=')
                    rhs = parts[-1].strip()
                else:
                    rhs = rest

                # myfunc(x) or myfunc
                name_part = rhs.split('(')[0].strip()
                # Split by space just in case 'function myfunc % comment'
                name_part = name_part.split(' ')[0].strip()
                # Split by % in case 'function myfunc%comment' (rare but possible)
                name_part = name_part.split('%')[0].strip()

                name = name_part
                break

    if name is None:
        # Maybe script? Use filename
        name = os.path.splitext(os.path.basename(filepath))[0]

    return [{'name': name, 'fullfilename': filepath}]


def findfunctionusefile(filepath, minfo):
    """
    Mock findfunctionusefile.
    Searches file for usage of function described in minfo.

    Args:
        filepath (str): File to search.
        minfo (dict): Info about function to search for.

    Returns:
        list of dicts: Usage info.
    """
    import os
    fuse = []
    fname = minfo['name']

    with open(filepath, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        idx = line.find(fname)
        if idx >= 0:
            # Found it
            # In MATLAB findfunctionusefile is more robust (tokenizing),
            # but string search is ok for mock.
            # Check if it's comment?
            incomments = line.strip().startswith('%')

            fuse.append({
                'fullfilename': filepath,
                'name': fname,
                'line': i + 1, # 1-based
                'character': idx + 1, # 1-based
                'incomments': incomments,
                'package_class_use': 0, # dummy
                'allcaps': 0 # dummy
            })

    return fuse
