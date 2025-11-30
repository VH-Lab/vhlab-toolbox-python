import numpy as np

def group_enumeration(m, n):
    """
    Enumerate combinations of groups.

    Args:
        m (list or numpy.ndarray): Vector with the number of members of each group.
        n (int): The group enumeration number to select.

    Returns:
        tuple: (g, max_n) where g is the group selection for enumeration n,
               and max_n is the maximum number of enumerations (prod(m)).
               g is 1-based indices if following MATLAB behavior?
               The example says:
               m = [1 3 1];
               n = 2;
               g is [1 2 1].
               This implies 1-based indexing for the result vector elements.
    """
    m = np.array(m, dtype=int)
    max_n = np.prod(m)

    if n > max_n:
        raise ValueError(f"n requested ({n}) exceeds maximum value possible ({max_n}).")
    if n < 1:
        raise ValueError(f"n must be 0...{max_n}.") # MATLAB error msg says 0..max_n but condition is n<1.

    g = np.ones(m.shape, dtype=int)

    inc = n - 1

    # digit = numel(m) -> len(m)
    digit = len(m) - 1 # 0-based index for python loop, but logic uses digit as index
    # MATLAB loop: digit = numel(m); while ... digit = digit-1.

    overflow = inc

    # MATLAB indexing: m(digit). digit goes from numel(m) down to 1.
    # Python indexing: digit goes from len(m)-1 down to 0.

    current_digit_idx = len(m) - 1

    while overflow > 0 and current_digit_idx >= 0:
        # digit_here = mod(g(digit)+overflow, m(digit));
        # g is initialized to ones. In MATLAB g(digit) is 1 initially.
        # In Python g is ones, so g[current_digit_idx] is 1.

        # We need to be careful with mod logic.
        # MATLAB: mod(1 + overflow, m). If result is 0, make it m.
        # Example: m=3. overflow=1. mod(2,3)=2.
        # Example: m=3. overflow=2. mod(3,3)=0 -> 3.
        # Example: m=3. overflow=3. mod(4,3)=1.

        val = g[current_digit_idx] + overflow
        m_val = m[current_digit_idx]

        digit_here = val % m_val
        if digit_here == 0:
            digit_here = m_val

        # overflow = ceil((g(digit)+overflow)/m(digit)-1);
        # Python ceil division?
        # overflow = ceil((1+overflow)/m - 1)
        # = ceil( (1+overflow)/m ) - 1
        # In Python: math.ceil(...)
        import math
        new_overflow = math.ceil(val / m_val) - 1

        g[current_digit_idx] = digit_here
        overflow = new_overflow
        current_digit_idx -= 1

    if overflow > 0:
         raise ValueError('Increment exceeded maximum count.')

    return g, max_n
