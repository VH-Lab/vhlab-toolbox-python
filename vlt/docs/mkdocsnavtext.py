from typing import List, Dict, Any, Union

def mkdocsnavtext(out: List[Dict[str, Any]], spaces: int) -> str:
    """
    Create navigation text for mkdocs.yml file from output of vlt.docs.matlab2markdown.

    Args:
        out: The output structure of vlt.docs.matlab2markdown (List of dicts).
        spaces: The number of spaces to indent.

    Returns:
        The navigation text.
    """

    t = ""

    for item in out:
        t += " " * spaces
        t += f"- {item['title']}"

        path_val = item.get('path')

        # Check if path is a list (nested struct) or string
        if not isinstance(path_val, list):
             t += f": '{path_val}'\n"
        else:
             t += ":\n"
             t += mkdocsnavtext(path_val, spaces + 2)

    return t
