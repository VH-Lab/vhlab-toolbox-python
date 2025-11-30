def columnize_struct(s_in):
    """
    Recursively processes substructures.
    In Python, this is mostly an identity operation for lists/dicts unless specific transformation is needed.
    """
    if isinstance(s_in, dict):
        s_out = s_in.copy()
        for k, v in s_out.items():
            if isinstance(v, dict) or isinstance(v, list):
                 s_out[k] = columnize_struct(v)
        return s_out
    elif isinstance(s_in, list):
        return [columnize_struct(x) for x in s_in]
    else:
        return s_in
