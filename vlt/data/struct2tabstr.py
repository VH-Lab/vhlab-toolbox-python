def struct2tabstr(a):
    """
    STRUCT2TABSTR - convert a struct to a tab-delimited string

    S = vlt.data.struct2tabstr(A)

    Given a dict A, this function creates a tab-delimited string with the values of the structure.
    """
    s = ''

    # We use keys as fieldnames
    keys = list(a.keys())

    for key in keys:
        val = a[key]
        if isinstance(val, str):
            s += '\t' + val
        else:
             # Convert to string representation
             # MATLAB uses mat2str which is close to str() or repr() but for matrices.
             # For simple scalars str() is fine.
             s += '\t' + str(val)

    if s.startswith('\t'):
        s = s[1:]

    return s
