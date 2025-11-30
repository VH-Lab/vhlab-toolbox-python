import numpy as np

def findrowvec(a, b):
    """
    FINDROWVEC - finds the occurrence of a complete row in a matrix

    I = vlt.data.findrowvec(A,B)

    Given a row vector B and a matrix A that has the same number of columns as B,
    I will be all rows such that all elements of A(i,:) equal those of B.

    Returns:
        indices: Array of indices (0-based) where the row matches.
    """

    a = np.array(a)
    b = np.array(b)

    if b.ndim == 1:
        b = b.reshape(1, -1)

    if a.shape[1] != b.shape[1]:
        raise ValueError("A and B must have the same number of columns.")

    # Check rows
    # a == b broadcasts b across a rows.
    # all(axis=1) checks if all elements in row match

    matches = np.all(a == b, axis=1)
    indices = np.where(matches)[0]

    return indices
