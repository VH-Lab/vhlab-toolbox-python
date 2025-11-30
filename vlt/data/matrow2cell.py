import numpy as np

def matrow2cell(x):
    """
    Convert a matrix into a list of row vectors.
    Equivalent to MATLAB's matrow2cell(x).

    x: Input matrix (numpy array).
    Returns: A list where each element is a 1xN numpy array representing a row of x.
    """
    x = np.array(x)

    if x.ndim == 1:
        # Treat 1D array as a single row vector
        return [x.reshape(1, -1)]

    output = []
    for i in range(x.shape[0]):
        output.append(x[i, :].reshape(1, -1))

    return output
