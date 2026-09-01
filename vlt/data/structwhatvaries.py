import numpy as np

def _isequaln(a, b):
    """
    NaN-aware equality, mirroring MATLAB's ISEQUALN.

    Equal shape and equal entries, except that NaN compares equal to NaN.
    This is the comparison MATLAB's vlt.data.structwhatvaries switched to in
    VH-Lab/vhlab-toolbox-matlab#137 (item 3); it is kept private here because
    the decision there was to change the call site, not vlt.data.eqlen.
    """
    aa = np.asarray(a)
    bb = np.asarray(b)

    if aa.shape != bb.shape:
        return False

    # equal_nan is only meaningful -- and only accepted -- for inexact dtypes.
    if aa.dtype.kind in 'fc' and bb.dtype.kind in 'fc':
        return bool(np.array_equal(aa, bb, equal_nan=True))

    return bool(np.array_equal(aa, bb))

def structwhatvaries(list_of_structures):
    """
    STRUCTWHATVARIES - Identify what varies among a list of structure objects

    DESCR = vlt.data.structwhatvaries(LISTOFSTRUCTURES)

    Given a list of structures (dicts), returns a list of the fieldnames that vary in
    value across the list.

    NaN semantics: values are compared with NaN-aware equality (NaN equals
    NaN), so a field that is NaN in *every* structure is NOT reported as
    varying. This matches the MATLAB toolbox, whose structwhatvaries compares
    with ISEQUALN; see VH-Lab/vhlab-toolbox-matlab#137 (item 3), which decided
    to fix this at the call site rather than in eqlen, and VH-Lab/NDI-matlab#902.

    vlt.data.eqlen is deliberately NOT used here and keeps its own
    NaN-not-equal semantics, exactly as MATLAB's EQLEN does. Changing this
    function without changing eqlen keeps the two ports symmetric.
    """
    descr = []

    if not isinstance(list_of_structures, list):
        raise TypeError('list_of_structures must be a list')

    for s in list_of_structures:
        if not isinstance(s, dict):
            raise TypeError('All entries of list_of_structures must be of type dict.')

    if len(list_of_structures) == 0:
        return descr

    fn1 = set(list_of_structures[0].keys())

    for i in range(1, len(list_of_structures)):
        s2 = list_of_structures[i]
        fn2 = set(s2.keys())

        # fields in s2 not in s1
        fn2_not_fn1 = fn2 - fn1
        # fields in s1 not in s2
        fn1_not_fn2 = fn1 - fn2

        descr.extend(list(fn2_not_fn1))
        descr.extend(list(fn1_not_fn2))

        bothfn = fn1.intersection(fn2)

        for field in bothfn:
            val1 = list_of_structures[0][field]
            val2 = s2[field]
            if not _isequaln(val1, val2):
                descr.append(field)

    # Unique and sort
    return sorted(list(set(descr)))
