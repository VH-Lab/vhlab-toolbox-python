def struct2namevaluepair(thestruct):
    """
    Convert a dictionary to a list of name/value pairs.
    """
    nv = []
    if not thestruct:
        return nv

    for k, v in thestruct.items():
        nv.append(k)
        nv.append(v)
    return nv
