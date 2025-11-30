import numpy as np

def value2sample(v, sr, v1):
    """
    vlt.signal.value2sample - give the sample number corresponding to a quantity that is sampled at a fixed rate (value2sample)

    s = value2sample(v, sr, v1)

    Given a value (or array of values) that are sampled at a fixed sampling
    rate sr (in samples/sec), and given the value of sample number 1,
    returns the sample numbers.

    See also: vlt.signal.sample2value

    Example:
       s = vlt.signal.value2sample(1, 1000, 0) # s is 1001

    Note: Python uses 0-based indexing. However, if this function is intended to
    return "sample numbers" which might be 1-based in MATLAB, we should clarify.
    MATLAB code: s = 1+sr*(double(v)-v1);
    If v=v1, s=1.
    If v=v1 + 1/sr, s=2.

    If we want 1-based sample numbers (compatible with MATLAB outputs), we keep it.
    But usually in Python we want 0-based indices.
    However, "sample number" is often abstract.
    Memory says: "Ported functions where MATLAB indices are returned ... use 1-based indexing to preserve direct compatibility with MATLAB algorithms and test expectations."
    So I will return 1-based indices as per memory instruction.
    """
    v = np.asarray(v)
    s = 1 + sr * (v - v1)
    return s
