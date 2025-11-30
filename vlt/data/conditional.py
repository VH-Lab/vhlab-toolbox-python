def conditional(test, a, b):
    """
    Return A or B depending on result of a true/false test.
    test > 0 -> a, else b.
    """
    if test > 0:
        return a
    else:
        return b
