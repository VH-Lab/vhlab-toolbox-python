
def structfullfields(s, prefix=''):
    """
    STRUCTFULLFIELDS - return full field names for structures and substructures

    FN = vlt.data.structfullfields(S)

    Returns the field names of a structure S, including substructures.

    For example, if a structure A has fields AA and AB, and AA is a structure
    with fields AAA and AAB, then FN is ['A.AA.AAA', 'A.AA.AAB', 'A.AB'].

    """
    if not isinstance(s, dict):
         raise TypeError('This function only works for dictionaries (structs).')

    out_fn = []
    keys = list(s.keys())

    for key in keys:
        full_key = prefix + key
        out_fn.append(full_key)
        v = s[key]
        if isinstance(v, dict):
            newfn = structfullfields(v, prefix + key + '.')
            out_fn.extend(newfn)

    return out_fn
