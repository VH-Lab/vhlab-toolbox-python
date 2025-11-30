from typing import Tuple, List, Optional

def line_n(s: str, n: int, **kwargs) -> Tuple[str, int, List[int]]:
    """
    Get the Nth line of a character string.

    Args:
        s: The input string.
        n: The 1-based line number to retrieve.
        **kwargs:
            eol (str): End of line character (default: '\n')
            eol_marks (List[int]): Pre-calculated positions of EOL characters.

    Returns:
        A tuple containing:
        - The string contents of the Nth line (without EOL).
        - The 1-based position of the beginning of the Nth line.
        - The locations of all EOL marks (1-based indices).

    Raises:
        ValueError: If n < 1 or n > number of lines.
    """

    eol = kwargs.get('eol', '\n')
    eol_marks = kwargs.get('eol_marks', None)

    if eol_marks is None:
        eol_marks = []
        for i, char in enumerate(s):
            if char == eol:
                eol_marks.append(i + 1) # 1-based index

        # If the last character is not eol, add a virtual eol at end+1
        if not eol_marks or eol_marks[-1] != len(s) + 1:
             # Actually, MATLAB implementation checks: if isempty(eol_marks) | (eol_marks(end)~=length(str))
             # eol_marks are indices in MATLAB (1-based).
             # if str is 'abc\n', length is 4. eol at 4.
             # if str is 'abc', length is 3. eol not found or marks empty.
             # MATLAB adds length(str)+1.

             # In Python: 'abc\n' len 4. index of \n is 3. 1-based is 4.
             # 'abc' len 3.

             # Check last mark
             if not eol_marks or eol_marks[-1] != len(s): # Wait, if eol is last char.
                 # Python len('abc\n') is 4.
                 # eol_marks will have 4.
                 # If string ends with \n, we are good?
                 # MATLAB: eol_marks(end)~=length(str).
                 # If 'abc\n', length is 4. eol at 4. 4==4.
                 # If 'abc', length is 3. eol_marks empty.
                 # Then adds length+1 = 4.

                 # So if string is 'abc', marks becomes [4].
                 # If string is 'abc\n', marks is [4].

                 # Wait, if 'abc\n', line 1 is 'abc'.
                 # If 'abc', line 1 is 'abc'.

                 if not s.endswith(eol):
                      eol_marks.append(len(s) + 1)

    if n > len(eol_marks):
        raise ValueError(f"Requested line {n} of a string with only {len(eol_marks)} lines.")

    if n < 1:
        raise ValueError("Line request cannot be less than 1")

    if n == 1:
        pos = 1
    else:
        pos = eol_marks[n-2] + 1 # n-1 th mark. In python list n-2.

    # extract string
    # pos is 1-based start.
    # end is eol_marks[n-1] - 1 (exclude eol)

    # Python slice: [start-1 : end]
    # start index: pos - 1
    # end index: eol_marks[n-1] - 1

    start_idx = pos - 1
    end_idx = eol_marks[n-1] - 1

    # If the mark was added virtually (len+1), then end_idx is len.
    # s[0:3] -> 'abc'

    line_n_str = s[start_idx:end_idx]

    return line_n_str, pos, eol_marks
