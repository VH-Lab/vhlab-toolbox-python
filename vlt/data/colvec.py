import numpy as np

def colvec(x):
    """
    Return a matrix reshaped as a column vector.
    """
    x = np.array(x)
    return x.flatten().reshape(-1, 1)
