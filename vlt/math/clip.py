def clip(a, clipvar):
    """
    Clip values between a low and a high limit.

    b = clip(a, clipvar)

    Return a variable b, the same size as a, except that all values of
    a that are below clipvar[0] are set to the value clipvar[0], and all values that
    are above clipvar[1] are set to clipvar[1].

    Example:
        b = clip([-float('inf'), 0, 1, 2, 3, float('inf')], [1, 2])
        # returns b = [1, 1, 1, 2, 2, 2]
    """
    import numpy as np

    if hasattr(a, "__len__"):
        a_arr = np.array(a)
        return np.clip(a_arr, clipvar[0], clipvar[1])
    else:
        return max(min(a, clipvar[1]), clipvar[0])
