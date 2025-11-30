import numpy as np

def rowvec(x):
    """
    Return a matrix reshaped as a row vector.
    """
    x = np.array(x)
    return x.flatten().reshape(1, -1)
