from .struct2namevaluepair import struct2namevaluepair
import inspect

def assign(*args):
    """
    Simulates vlt.data.assign.
    Returns a dictionary of assignments.
    Usage:
        d = assign('var1', val1, 'var2', val2)
        locals().update(d)
    """
    varargin = list(args)
    if len(varargin) == 1:
        if isinstance(varargin[0], dict):
            varargin = struct2namevaluepair(varargin[0])
        elif isinstance(varargin[0], list) or isinstance(varargin[0], tuple):
            varargin = list(varargin[0])

    d = {}
    for i in range(0, len(varargin), 2):
        if i+1 < len(varargin):
            var = varargin[i]
            val = varargin[i+1]
            if isinstance(var, str):
                d[var] = val

    # Attempt to update caller's locals (optional, unsafe)
    try:
        frame = inspect.currentframe().f_back
        frame.f_locals.update(d)
    except:
        pass

    return d
