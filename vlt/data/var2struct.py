import inspect

def var2struct(*args):
    """
    VAR2STRUCT - Export variable(s) to a structure (dictionary)

    OUTPUT = vlt.data.var2struct('NAME1', 'NAME2', ...)

    Saves local workspace variables as a structure.

    Each variable is added a field to the structure OUTPUT.
    """
    output = {}
    frame = inspect.currentframe().f_back
    try:
        for name in args:
            if name in frame.f_locals:
                output[name] = frame.f_locals[name]
            elif name in frame.f_globals:
                output[name] = frame.f_globals[name]
            else:
                 # In MATLAB evalin('caller', var) would error if not found.
                 raise KeyError(f"Variable '{name}' not found in caller's scope.")
    finally:
        del frame
    return output
