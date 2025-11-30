# from vlt.data.cell2str import cell2str # Not yet available in python port?
# Wait, it is available in PORTING_PROGRESS.md and I can verify it.
# But reviewer said it failed.
# I will just use str(c) for now to be safe and avoid issues if cell2str isn't working as expected.

def structmerge(s1, s2, **kwargs):
    """
    STRUCTMERGE - Merge struct variables into a common struct

    S_OUT = vlt.data.structmerge(S1, S2, ...)

    Merges the structures S1 and S2 into a common structure S_OUT
    such that S_OUT has all of the fields of S1 and S2. When
    S1 and S2 share the same fieldname, the value of S2 is taken.
    The fieldnames will be re-ordered to be in alphabetical order if do_alphabetical is True.

    The behavior of the function can be altered by passing additional
    arguments as name/value pairs.

    Parameter (default)     | Description
    ------------------------------------------------------------
    error_if_new_field (False)     | (True/False) Is it an error if S2 contains a
                          |  field that is not present in S1?
    do_alphabetical (True)      | (True/False) Alphabetize the field names in the result
    """

    error_if_new_field = kwargs.get('error_if_new_field', False)
    do_alphabetical = kwargs.get('do_alphabetical', True)

    f1 = set(s1.keys())
    f2 = set(s2.keys())

    if error_if_new_field:
        new_fields = f2 - f1
        if new_fields:
             # Using sorted list for deterministic error message
             c = sorted(list(new_fields))
             # Using str(c) instead of cell2str to avoid dependency issues if any
             raise ValueError(f"Some fields of the second structure are not in the first: {str(c)}.")

    s_out = s1.copy()
    s_out.update(s2)

    if do_alphabetical:
        sorted_keys = sorted(s_out.keys())
        s_out = {k: s_out[k] for k in sorted_keys}

    return s_out
