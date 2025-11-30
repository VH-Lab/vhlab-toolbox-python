def intseq2str(A, **kwargs):
    """
    INTSEQ2STR - Convert an array of integers to a compact string, maintaining sequence

    str_out = vlt.string.intseq2str(A, **kwargs)

    Converts the sequence of integers in array A to a compact, human-readable
    sequence with '-' indicating inclusion of a series of numbers and commas
    separating discontinuous numbers.

    Parameters:
    A (array-like): Array of integers.
    **kwargs:
        sep (str): The separator between the numbers (default ',')
        seq (str): The character that indicates a sequential run of numbers (default '-')

    Returns:
    str_out (str): Compact string representation.

    Example:
        A = [1, 2, 3, 7, 10]
        str_out = intseq2str(A)
        # str_out == '1-3,7,10'
    """

    sep = kwargs.get('sep', ',')
    seq = kwargs.get('seq', '-')

    # Handle implicit truthiness of numpy arrays
    # "The truth value of an array with more than one element is ambiguous"
    # Use len() check.

    if len(A) == 0:
        return ''

    import numpy as np
    A = np.asarray(A)
    if A.size == 0:
        return ''

    str_out = ""

    i = 0
    while i < len(A):
        # Start of a run
        start_val = A[i]

        # Find how far the run of +1 goes
        j = i
        while j < len(A) - 1 and A[j+1] - A[j] == 1:
            j += 1

        # Run is from i to j (inclusive)
        end_val = A[j]

        if j > i:
            # We have a sequence
            str_out += f"{start_val}{seq}{end_val}"
        else:
            # Single value
            str_out += f"{start_val}"

        # Add separator if not last
        if j < len(A) - 1:
            str_out += sep

        i = j + 1

    return str_out
