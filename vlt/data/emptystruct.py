def emptystruct(*args):
    """
    EMPTYSTRUCT - Create a structure with given fieldnames that is empty

    S = vlt.data.emptystruct(fieldname1, fieldname2, ...);
      or
    S = vlt.data.emptystruct({fieldname1, fieldname2, ...});

    Creates an empty structure with a given list of field names.

    In Python, this returns an empty list, as an empty struct array in MATLAB
    corresponds to an empty list of dictionaries. The fields are not enforced
    on the empty list itself, but this function is provided for compatibility.
    """
    # In MATLAB, s([]) with fields results in a 0x0 struct array with fields.
    # In Python, we don't have a direct equivalent of a 0-length list that knows its schema.
    # We will return an empty list.
    return []
