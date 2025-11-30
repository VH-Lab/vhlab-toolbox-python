def line_n(str_in, n, **kwargs):
    """
    Get the Nth line of a character string.

    line_n_str, pos, eol_marks = line_n(str, n, ...)

    Returns the Nth line of a multiline string str_in.
    line_n_str is the string contents of the Nth line,
    without the end of line character.
    The position of the beginning of the Nth line within the
    string str_in is returned in pos (1-based index).
    The function also returns all of the locations of the
    end of line marks eol_marks (1-based index).

    If the last character of str_in is not an end-of-line, then the function
    adds an end-of-line character to the end of the string (and this is returned
    in eol_marks).

    The behavior of the function can be altered by adding
    name/value pairs:
    eol ('\n')            : End of line character, could also use '\r'
    eol_marks ([])        : If it is non-empty, then the program
                          :   skips the search for eol_marks and
                          :   uses the provided variable. This is useful
                          :   if the user is going to call line_n
                          :   many times; one can save the search time
                          :   in subsequent calls.
    """

    eol = '\n'
    eol_marks = []

    if 'eol' in kwargs:
        eol = kwargs['eol']
    if 'eol_marks' in kwargs:
        eol_marks = kwargs['eol_marks']

    if not eol_marks:
        eol_marks = [i + 1 for i, char in enumerate(str_in) if char == eol]
        if not eol_marks or (len(str_in) > 0 and eol_marks[-1] != len(str_in)):
             eol_marks.append(len(str_in) + 1)

    if n > len(eol_marks):
        raise Exception(f"Requested line {n} of a string with only {len(eol_marks)} lines.")

    if n < 1:
        raise Exception("Line request cannot be less than 1")

    if n == 1:
        pos = 1
    else:
        pos = eol_marks[n-2] + 1

    start_idx = pos - 1
    end_idx = eol_marks[n-1] - 1

    if end_idx > len(str_in):
        end_idx = len(str_in)

    line_n_str = str_in[start_idx:end_idx]

    return line_n_str, pos, eol_marks
