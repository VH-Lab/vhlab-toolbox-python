import inspect

def workspace2struct():
    """
    WORKSPACE2STRUCT - Export the current workspace to a structure

    OUTPUT = vlt.data.workspace2struct()

    Saves the local workspace as a structure for easy export.

    Each variable is added a field to the structure OUTPUT.
    """
    output = {}
    frame = inspect.currentframe().f_back
    try:
        for name, val in frame.f_locals.items():
            if not name.startswith('_'): # Heuristic to exclude internal python vars
                output[name] = val
    finally:
        del frame
    return output
