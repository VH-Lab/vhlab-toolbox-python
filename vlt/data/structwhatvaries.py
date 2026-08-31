import numpy as np


def _equal_including_nan(x, y):
    """Same shape and contents, treating NaN as equal to itself.

    The numpy equivalent of MATLAB's isequaln, and of vlt.data.eqlen except
    for the NaN handling. equal_nan is unsupported for object and string
    dtypes, where NaN cannot occur anyway, so fall back for those.
    """
    x = np.asarray(x)
    y = np.asarray(y)
    if x.shape != y.shape:
        return False
    try:
        return bool(np.array_equal(x, y, equal_nan=True))
    except (TypeError, ValueError):
        return bool(np.array_equal(x, y))


def structwhatvaries(list_of_structures):
    """
    STRUCTWHATVARIES - Identify what varies among a list of structure objects

    DESCR = vlt.data.structwhatvaries(LISTOFSTRUCTURES)

    Given a list of structures (dicts), returns a list of the fieldnames that vary in
    value across the list.

    NaN semantics: equality is NaN-aware, so a field that is NaN in every
    structure counts as constant and is NOT reported as varying. Resolved in
    VH-Lab/vhlab-toolbox-matlab#137 (item 3); the MATLAB port makes the
    matching change, using isequaln in its own structwhatvaries.

    The fix is deliberately here rather than in vlt.data.eqlen, mirroring
    MATLAB: eqlen is widely used, and changing its NaN semantics would ripple
    much further than this one call site. VH-Lab/NDI-matlab#902 took the same
    route. Keep the two ports in step -- they are meant to agree.
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
            if not _equal_including_nan(val1, val2):
                descr.append(field)

    # Unique and sort
    return sorted(list(set(descr)))
