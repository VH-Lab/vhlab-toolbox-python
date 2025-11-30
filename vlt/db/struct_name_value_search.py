from typing import List, Dict, Any, Optional

def struct_name_value_search(thestruct: List[Dict[str, Any]], thename: str, makeerror: bool = True) -> Any:
    """
    Search a struct (list of dicts) with fields 'name' and 'value'.

    Args:
        thestruct: A list of dictionaries (simulating a struct array), where each dictionary
                   must have 'name' and 'value' keys.
        thename: The name to search for in the 'name' field.
        makeerror: Whether to raise an error if the name is not found (default: True).

    Returns:
        The value associated with the found name.

    Raises:
        ValueError: If `thestruct` entries lack 'name' or 'value' fields, or if `thename` is not found
                    and `makeerror` is True.
    """

    # Check if the list is empty, if so, we can't check fields but it is also not found
    if not thestruct:
         if makeerror:
            raise ValueError(f"No matching entries for {thename} were found (structure is empty).")
         return None

    # Check fields in the first element (assuming consistent structure as per MATLAB struct array)
    # However, Python list of dicts might vary, so we should check each or just check on access.
    # The MATLAB code checks fields using `isfield` which works on the whole struct array.
    # In Python, we will iterate and check.

    # Actually, the MATLAB code checks:
    # if ~isfield(thestruct,'name') error...
    # if ~isfield(thestruct,'value') error...

    # We should verify that at least one element has these keys or enforce it on all?
    # Usually in these ports, we assume the input follows the structure.
    # Let's check the first element to be safe, or just proceed and catch KeyError if we want strictly
    # mimic the "isfield" check before searching.

    # Let's iterate to find the match.

    found_index = -1
    found_value = None

    for i, entry in enumerate(thestruct):
        if 'name' not in entry:
             raise ValueError("THESTRUCT must have a field named 'name'.")
        if 'value' not in entry:
             raise ValueError("THESTRUCT must have a field named 'value'.")

        if entry['name'] == thename:
            found_value = entry['value']
            found_index = i
            break

    if found_index != -1:
        return found_value
    else:
        if makeerror:
            raise ValueError(f"No matching entries for {thename} were found.")
        return None
