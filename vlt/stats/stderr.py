import numpy as np

def stderr(data):
    """
    STDERR - Standard error of a vector of data

    se = vlt.stats.stderr(data)

    Computes standard error of each column.

    se = std(data)./repmat(sqrt(size(data,1)),1,size(data,2));

    Note: MATLAB std uses N-1 normalization by default. NumPy std uses N by default.
    We must use ddof=1 to match MATLAB.
    """
    data = np.asarray(data)

    if data.ndim == 1:
        # If vector, compute scalar stderr
        if data.size == 0:
            return np.nan
        # MATLAB std on vector returns scalar std.
        return np.std(data, ddof=1) / np.sqrt(data.size)
    else:
        # If matrix, compute per column
        # MATLAB std operates along first non-singleton dimension (rows usually)
        # Assuming data is (N, M)
        if data.shape[0] == 0:
            return np.full((1, data.shape[1]), np.nan)

        std_val = np.std(data, axis=0, ddof=1)
        # sqrt(N)
        n = data.shape[0]
        se = std_val / np.sqrt(n)

        # MATLAB returns a row vector if input is a matrix
        return se
