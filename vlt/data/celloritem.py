def celloritem(var, index=0, useindexforvar=False):
    """
    Returns the ith element of a list, or a single item.
    index is 0-based in Python.
    """
    if isinstance(var, list) or isinstance(var, tuple):
        if index < len(var):
            return var[index]
        else:
            raise IndexError("Index out of range")
    else:
        if useindexforvar:
            try:
                return var[index]
            except:
                return var
        else:
            return var
