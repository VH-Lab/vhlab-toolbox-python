import numpy as np

def rescale(vals, int1, int2, noedge=False):
    """
    Rescale a quantity to a new interval.

    Args:
        vals (numpy.ndarray or float): Values to rescale.
        int1 (list): Input interval [a, b].
        int2 (list): Output interval [c, d].
        noedge (bool): If True, do not clip values. Default False.
                       MATLAB uses 'noclip' string or checks nargin.
                       Here we use explicit bool argument.
                       If 'noclip' is passed as string, we should handle it?
                       The function signature in MATLAB is `rescale(vals, int1, int2, noedge)`.
                       If `noedge` is 'noclip' (or anything truthy?)
                       Code: `if nargin<4 ... clip ... end`.
                       So if ANY argument is passed as 4th arg, clipping is skipped?
                       Wait.
                       MATLAB:
                       if nargin<4,
                           clip
                       end
                       So if 4 arguments are provided, it SKIPS clipping.
                       So `rescale(v, i1, i2, 'clip')` would SKIP clipping?
                       That seems counter-intuitive but that's what `if nargin<4` does.
                       The doc says: `rescale(..., 'noclip')` will do the same but not clip.
                       It doesn't say what happens if you pass something else.
                       It seems presence of 4th argument disables clipping.

    Returns:
        numpy.ndarray: Rescaled values.
    """
    vals = np.array(vals, dtype=float)
    int1 = np.array(int1, dtype=float)
    int2 = np.array(int2, dtype=float)

    # newvals = (int2(1)+((vals-int1(1))./diff(int1))*diff(int2));
    # diff(int1) is int1[1] - int1[0]

    diff1 = int1[1] - int1[0]
    diff2 = int2[1] - int2[0]

    newvals = int2[0] + ((vals - int1[0]) / diff1) * diff2

    # Check if we should clip
    # In MATLAB, if nargin < 4, we clip.
    # So if `noedge` is NOT provided (default), we clip.
    # If `noedge` IS provided (Truthy or not?), we SKIP clipping.
    # Wait, `noedge` argument name implies "no edge clipping".
    # In my python signature `noedge=False`.
    # If I call `rescale(..., noedge='noclip')`, noedge is True-ish.
    # If I call `rescale(...)`, noedge is False.
    # So if `noedge` is False, we CLIP?
    # No, logic: `if nargin < 4` (argument missing) -> CLIP.
    # So if argument is PRESENT, NO CLIP.
    # So if I pass `noedge=True`, I should NOT clip.
    # If I pass `noedge=False` (default), I SHOULD clip.
    # But wait, `noedge` is just a name I gave.
    # The MATLAB code doesn't check the value of the 4th arg.

    if not noedge:
        # Clip
        # newvals(find(newvals>int2(2))) = int2(2);
        # newvals(find(newvals<int2(1))) = int2(1);
        # Note: int2[1] is max, int2[0] is min usually?
        # Assuming int2 is [min max].
        # But if int2 is reversed [max min], diff is negative.
        # The logic `> int2(2)` implies int2(2) is the upper bound?
        # If int2 = [10 0], diff is -10.
        # vals mapped.
        # `newvals > int2(2)` -> `newvals > 0`.
        # `newvals < int2(1)` -> `newvals < 10`.
        # This seems to assume int2 is [min max].
        # If int2 is [10 0], then `>0` sets to 0. `<10` sets to 10.
        # This effectively clamps to range [0, 10].

        # We can use np.clip if int2 is sorted.
        # But let's follow logic exactly.

        newvals[newvals > int2[1]] = int2[1]
        newvals[newvals < int2[0]] = int2[0]

    return newvals
