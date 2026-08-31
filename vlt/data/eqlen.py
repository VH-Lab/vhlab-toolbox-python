import numpy as np

def eqlen(x, y):
    """
    vlt.data.eqlen  Returns 1 if objects to compare are equal and have same size

      B = vlt.data.eqlen(X,Y)

    Returns 1 iff X and Y have the same length and all of the entries in X and
    Y are the same.

    NaN semantics: NaN does not compare equal to itself, so
    eqlen(nan, nan) is False and eqlen([1, nan], [1, nan]) is False. This
    matches the MATLAB toolbox, whose eqlen bottoms out in `x==y`. Callers
    that want NaN-aware equality should use something like
    numpy.array_equal(x, y, equal_nan=True) at the call site rather than
    changing this function -- see VH-Lab/vhlab-toolbox-matlab#137 (item 3),
    where the same decision is pending for MATLAB, and VH-Lab/NDI-matlab#902,
    which switched to isequaln at its own call sites for this reason.
    """

    # Handle scalar / array differences
    x = np.array(x)
    y = np.array(y)

    if x.shape != y.shape:
        return False

    return np.array_equal(x, y)
