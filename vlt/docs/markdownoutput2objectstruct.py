from typing import List, Dict, Any, Union
from vlt.data.emptystruct import emptystruct

def markdownoutput2objectstruct(markdown_output: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Create a list of all objects and their paths for making mkdocs links.

    Given a MARKDOWN_OUTPUT structure returned from vlt.docs.matlab2markdown, creates a structure with
    fields 'object' and 'path'. 'object' has the name of each object, and 'path' has its absolute path.

    Args:
        markdown_output: A list of dictionaries representing the markdown structure.

    Returns:
        A list of dictionaries with keys 'object', 'path', and 'url_prefix'.
    """

    objectstruct = [] # equivalent to vlt.data.emptystruct('object','path','url_prefix') in Python context

    for item in markdown_output:
        # In MATLAB: if ~isstruct(markdown_output(i).path)
        # In Python, we check if 'path' is a list (nested struct) or a string/primitive

        path_val = item.get('path')

        # If path_val is a list, it means it's a nested structure (recursive case)
        # If it is a string (or None/not a list), it's a leaf.
        # However, looking at the MATLAB code:
        # isstruct(markdown_output(i).path) -> recurses
        # else -> treats as leaf

        if not isinstance(path_val, list):
            newentry = {
                'object': item.get('title'),
                'path': path_val,
                'url_prefix': item.get('url_prefix')
            }
            objectstruct.append(newentry)
        else:
            # Recursion
            # objectstruct = cat(2,objectstruct, vlt.docs.markdownoutput2objectstruct(markdown_output(i).path));
            recursive_result = markdownoutput2objectstruct(path_val)
            objectstruct.extend(recursive_result)

    return objectstruct
