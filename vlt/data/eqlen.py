import numpy as np

def eqlen(x, y):
    """
    vlt.data.eqlen  Returns 1 if objects to compare are equal and have same size

      B = vlt.data.eqlen(X,Y)

    Returns 1 iff X and Y have the same length and all of the entries in X and
    Y are the same.
    """

    # Handle scalar / array differences
    x = np.array(x)
    y = np.array(y)

    if x.shape != y.shape:
        return False

    return np.array_equal(x, y)
