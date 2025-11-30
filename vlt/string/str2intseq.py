def str2intseq(str_in, **kwargs):
    """
    STR2INTSEQ - Recover a sequence of integers from a string

    a = vlt.string.str2intseq(str_in, **kwargs)

    Given a string that specifies a list of integers, with a dash ('-') indicating a run of
    sequential integers in order, and a comma (',') indicating integers that are not
    (necessarily) sequential.

    Parameters:
    str_in (str): The string to parse.
    **kwargs:
        sep (str): The separator between the numbers (default ',')
        seq (str): The character that indicates a sequential run of numbers (default '-')

    Returns:
    a (list): List of integers.

    Example:
        str_in = '1-3,7,10,12'
        a = str2intseq(str_in)
        # a == [1, 2, 3, 7, 10, 12]
    """
    sep = kwargs.get('sep', ',')
    seq = kwargs.get('seq', '-')

    a = []

    if not str_in:
        return a

    parts = str_in.split(sep)

    for part in parts:
        part = part.strip()
        if not part:
            continue

        if seq in part:
            # Handle sequence
            # Usually "start-end"
            subparts = part.split(seq)
            if len(subparts) == 2:
                try:
                    start = int(subparts[0])
                    end = int(subparts[1])
                    if start <= end:
                        a.extend(range(start, end + 1))
                    else:
                        pass
                except ValueError:
                    # Could not parse integers. Ignore?
                    pass
            else:
                pass
        else:
            # Single integer
            try:
                val = int(part)
                a.append(val)
            except ValueError:
                pass

    return a
