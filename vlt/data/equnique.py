import numpy as np

# Improved implementation handling numpy arrays more gracefully
def _is_equal(a, b):
    try:
        return np.array_equal(a, b)
    except:
        return a == b

def equnique(in_data):
    """
    EQUNIQUE - Return unique elements of an arbitrary class using equality

    OUT = vlt.data.equnique(IN)

    Returns the unique elements of an object array IN as a list.

    Uses equality (==) to test for equality, rather than hash.
    This is useful for objects that don't verify hashability or where
    reference equality isn't what is desired.
    """
    if np.isscalar(in_data):
        return [in_data]

    # Check if it is a list or array
    if isinstance(in_data, (list, tuple, np.ndarray)):
        out = []
        for item in in_data:
            found = False
            for seen in out:
                if _is_equal(item, seen):
                    found = True
                    break
            if not found:
                out.append(item)
        return out
    else:
        # Fallback for single object?
        return [in_data]
