import numpy as np

def findclosest(arr, v):
    """
    FINDCLOSEST - Find closest value in an array (using absolute value)

    [I,V] = vlt.data.findclosest(ARRAY,VALUE)

    Finds the index to the closest member of ARRAY to VALUE
    in absolute value. It returns the index in I and the value
    in V.  If ARRAY is empty, so are I and V.

    If there are multiple occurrences of VALUE within ARRAY,
    only the first is returned in I.

    Returns:
        tuple: (index, value). Returns (None, None) if array is empty.
    """

    arr = np.array(arr)
    if arr.size == 0:
        return None, None

    idx = np.nanargmin(np.abs(arr - v))
    val = arr.flatten()[idx] # flatten to handle if arr is MD, though usually vector

    return idx, val
