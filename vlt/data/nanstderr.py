import numpy as np

def nanstderr(x, dim=None):
    """
    Compute the standard error of the mean, ignoring NaNs.

    x: Input array
    dim: Dimension to operate along. If None, operates on the flattened array.
         If dim is specified, it works like standard numpy axis (0-based).
    """
    x = np.array(x)

    # Calculate count of non-NaN elements
    n = np.sum(~np.isnan(x), axis=dim)

    # Calculate standard deviation ignoring NaNs
    # MATLAB uses ddof=1 by default for std (sample standard deviation)
    s = np.nanstd(x, axis=dim, ddof=1)

    # Standard error = std / sqrt(n)
    return s / np.sqrt(n)
