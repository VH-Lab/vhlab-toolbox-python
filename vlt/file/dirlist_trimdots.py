from typing import List, Union, Dict, Any

def dirlist_trimdots(dirlist: Union[List[str], List[Dict[str, Any]]], output_struct: bool = False) -> Union[List[str], List[Dict[str, Any]]]:
    """
    Trim strings '.' or '..' from a list of directory strings.

    Args:
        dirlist: A list of strings (directory names) or a list of dictionaries (like os.scandir or MATLAB dir struct).
        output_struct: If True, and input is a list of dicts, returns a filtered list of dicts.

    Returns:
        Filtered list.
    """

    ignore_list = {'.', '..', '.DS_Store', '.git', '.svn', '__pycache__'}

    # Check if dirlist is a list of dicts (resembling MATLAB struct array from dir())
    is_struct = False
    if isinstance(dirlist, list) and len(dirlist) > 0 and isinstance(dirlist[0], dict):
        is_struct = True
    elif isinstance(dirlist, list) and len(dirlist) == 0:
         # Empty list, return empty
         return []

    if is_struct:
        if output_struct:
            return [d for d in dirlist if d.get('name') not in ignore_list]
        else:
            # Extract names and filter, but only directories?
            # MATLAB code: dirnumbers = find([dirlist.isdir]); dirlist = {dirlist(dirnumbers).name};
            # It implies if output_struct is False, we extract names of DIRECTORIES only.

            # We need to check if 'isdir' is a key or if we should just assume it's like struct.
            # If 'isdir' is present, use it.

            filtered_names = []
            for d in dirlist:
                if d.get('name') not in ignore_list:
                    if 'isdir' in d:
                        if d['isdir']:
                            filtered_names.append(d['name'])
                    else:
                        # If isdir is not present, maybe we should just include it?
                        # But the MATLAB code specifically does `find([dirlist.isdir])`.
                        # If the key is missing in Python dict, we probably shouldn't assume it is a dir?
                        # Or maybe we assume it is a simple struct with name.
                        # But strict porting suggests following logic.
                        pass
            return filtered_names

    if not isinstance(dirlist, list):
         raise ValueError("DIRLIST must be a list.")

    # List of strings
    return [d for d in dirlist if d not in ignore_list]
