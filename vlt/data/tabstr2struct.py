import re

def tabstr2struct(s, fields):
    """
    TABSTR2STRUCT - convert a tab-separated set of strings to a STRUCT entry

    A = vlt.data.tabstr2struct(S, FIELDS)

    Given a list of strings FIELDS of field names, creates a dict
    where the values of each field are specified in a tab-delimited string S.

    Each string is first examined to see if it is a number (using float).
    If so, then the value is stored as a float. Otherwise, the value is
    stored as a string.

    Exceptions:
      a) If the string happens to have two '/' characters or has the form 'yyyy-dd-mm', then it
         is assumed to be a date and is interpreted as a string.
    """

    a = {}

    # MATLAB implementation:
    # str = [char(9) s char(9)];
    # pos = findstr(str,char(9));
    # for i=1:length(fields)
    #   t = str(pos(i)+1:pos(i+1)-1);

    # This implies that `s` is treated as values separated by tabs.
    # If s = 'val1\tval2', and fields = ['f1', 'f2']
    # MATLAB: str = '\tval1\tval2\t'
    # pos = [1, 6, 11] (indices of tabs)
    # i=1: t = str(2:5) = 'val1'
    # i=2: t = str(7:10) = 'val2'

    # Python split('\t') on 'val1\tval2' -> ['val1', 'val2']
    # If empty fields: 'val1\t\tval3' -> ['val1', '', 'val3']

    # What if s starts/ends with tab?
    # s = '\tval1' -> split -> ['', 'val1']
    # MATLAB: str = '\t\tval1\t'
    # pos = [1, 2, 7]
    # i=1: t = str(2:1) = '' (empty)
    # i=2: t = str(3:6) = 'val1'

    # It seems MATLAB code assumes `s` does NOT include the surrounding tabs that represent the fields boundaries if they were joined?
    # Or does it?
    # Usually `s` is a line from a tab-delimited file, which might not have tabs at edges if values are there.
    # The MATLAB code forces tabs at edges to handle edge cases or to simplify parsing.

    # The crucial part is that `pos(i)` corresponds to the start of field i value.
    # `pos` indices are 1-based.
    # `str` has `\t` at pos[1], pos[2], ...
    # field i value is between pos[i] and pos[i+1].

    # This means if `s` is just `val1\tval2`,
    # str=`\tval1\tval2\t`.
    # pos=[1, 6, 11].
    # i=1: between 1 and 6 -> val1.
    # i=2: between 6 and 11 -> val2.

    # So basically it is splitting `s` by tab.

    parts = s.split('\t')

    # However, if `s` has fewer parts than `fields`, MATLAB code would error at `pos(i+1)` if `i+1 > length(pos)`.
    # We should handle this.

    for i, field in enumerate(fields):
        if i >= len(parts):
            # In MATLAB this would error.
            # But maybe we should just stop or fill with None/empty string?
            # The prompt doesn't specify. I'll stick to splitting and iterating.
            # If parts run out, we stop.
            break

        t = parts[i]

        # Check for date
        is_date = (t.count('/') > 1) or bool(re.search(r'(\s*)\d\d\d\d-\d\d-\d\d(\s*)', t))

        u = None
        if not is_date:
            try:
                if t.strip() == '': # Handle empty string explicitly
                    u = None
                else:
                    u = float(t)
            except ValueError:
                u = None

        if u is not None:
             a[field] = u
        else:
             a[field] = t

    return a
