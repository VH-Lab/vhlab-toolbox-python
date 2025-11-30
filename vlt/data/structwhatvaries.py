from vlt.data.eqlen import eqlen

def structwhatvaries(list_of_structures):
    """
    STRUCTWHATVARIES - Identify what varies among a list of structure objects

    DESCR = vlt.data.structwhatvaries(LISTOFSTRUCTURES)

    Given a list of structures (dicts), returns a list of the fieldnames that vary in
    value across the list.
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
            if not eqlen(val1, val2):
                descr.append(field)

    # Unique and sort
    return sorted(list(set(descr)))
