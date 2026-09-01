import numpy as np

def eqlen(x, y):
    """
    vlt.data.eqlen  Returns 1 if objects to compare are equal and have same size

      B = vlt.data.eqlen(X,Y)

    Returns 1 iff X and Y have the same length and all of the entries in X and
    Y are the same.

    NaN semantics: NaN does not compare equal to itself, so
    eqlen(nan, nan) is False and eqlen([1, nan], [1, nan]) is False. This
    matches the MATLAB toolbox, whose eqlen bottoms out in `x==y`. That is
    settled, not pending: VH-Lab/vhlab-toolbox-matlab#137 (item 3) decided to
    leave eqlen alone -- too many callers depend on it -- and to fix
    structwhatvaries at its call site instead, which vlt.data.structwhatvaries
    mirrors here. VH-Lab/NDI-matlab#902 took the same route with isequaln.
    Callers wanting NaN-aware equality should use something like
    numpy.array_equal(x, y, equal_nan=True) at their own call site.

    Known divergence from MATLAB: MATLAB's eqemp bottoms out in a literal
    `x==y`, which MATLAB does not define for cell arrays, so MATLAB's
    eqlen({'r','g','b'}, {'r','g','b'}) raises rather than returning a value
    (vhlab-toolbox-matlab#137, item 2). This port has no such operator gap --
    the equivalent call returns True. Cross-language comparisons should not
    expect an error here.
    """

    # Handle scalar / array differences
    x = np.array(x)
    y = np.array(y)

    if x.shape != y.shape:
        return False

    return np.array_equal(x, y)
