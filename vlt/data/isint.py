import numpy as np

def isint(X):
    """
    B = 1 iff X is a matrix of integers.
    """
    if isinstance(X, (int, np.integer)):
        return True
    if isinstance(X, float):
        return X.is_integer()

    # Handle list or tuple
    if isinstance(X, (list, tuple)):
        X = np.asarray(X)

    if isinstance(X, np.ndarray):
        if np.issubdtype(X.dtype, np.number):
            if np.isrealobj(X):
                 if not np.all(np.isfinite(X)):
                     return False
                 return np.all(X == np.fix(X))

    return False
