def partial_struct_match(A, B):
    """
    Returns True if structure A matches B for the fields present in B.
    B is the subset / template. A must contain all keys in B, and values must match.

    A, B: dictionaries (or objects acting like structs).
    """
    if not isinstance(A, dict) or not isinstance(B, dict):
        return A == B

    for k, v in B.items():
        if k not in A:
            return False
        if not partial_struct_match(A[k], v):
            return False
    return True
