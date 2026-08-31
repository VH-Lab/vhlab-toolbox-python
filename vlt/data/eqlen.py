import numpy as np

def eqlen(x, y):
    """
    vlt.data.eqlen  Returns 1 if objects to compare are equal and have same size

      B = vlt.data.eqlen(X,Y)

    Returns 1 iff X and Y have the same length and all of the entries in X and
    Y are the same.

    NaN semantics: NaN does not compare equal to itself, so eqlen(nan, nan)
    is False and eqlen([1, nan], [1, nan]) is False. This is deliberate, and
    matches the MATLAB toolbox, whose eqlen bottoms out in `x==y`.

    VH-Lab/vhlab-toolbox-matlab#137 (item 3) resolved this by making
    NaN-aware comparison the job of the call site rather than of eqlen:
    eqlen is used widely enough that changing it here would ripple far beyond
    the callers that care. vlt.data.structwhatvaries does exactly that, as did
    VH-Lab/NDI-matlab#902. Callers wanting NaN-aware equality should follow
    suit with numpy.array_equal(x, y, equal_nan=True).
    """

    # Handle scalar / array differences
    x = np.array(x)
    y = np.array(y)

    if x.shape != y.shape:
        return False

    return np.array_equal(x, y)
