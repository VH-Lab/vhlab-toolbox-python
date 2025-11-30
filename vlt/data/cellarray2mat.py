import numpy as np

def cellarray2mat(c):
    """
    Convert list of vectors to a matrix, filling with NaN.
    c: list of lists (or numpy arrays).
    """
    if not c:
        return np.array([])

    # Determine max length
    row = 0
    for item in c:
        if item is not None and hasattr(item, '__len__'):
            row = max(row, len(item))
        elif item is not None:
             # scalar
             row = max(row, 1)

    col = len(c)
    m = np.full((row, col), np.nan)

    for i in range(col):
        item = c[i]
        if item is not None:
             if hasattr(item, '__len__'):
                 l_item = list(item)
                 for j in range(len(l_item)):
                     if j < row:
                         m[j, i] = l_item[j]
             else:
                 if 0 < row:
                     m[0, i] = item

    return m
