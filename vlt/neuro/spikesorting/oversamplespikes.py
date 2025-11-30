import numpy as np
from scipy.interpolate import interp1d

def oversamplespikes(spikeshapes, upsamplefactor, t=None):
    """
    Oversample spike waveforms using spline interpolation.

    [SPIKESHAPESUP, TUP] = oversamplespikes(SPIKESHAPES, UPSAMPLEFACTOR, [T])

    Inputs:
        spikeshapes: an NxMxD matrix of spikes shapes; N is the number of
            spikes, M is the number of samples per spike, and D is the number
            of dimensions (e.g., D=1 for a single channel recording).
        upsamplefactor: the number of times to oversample (e.g., 5)
        t: (optional), the relative time values within each spike sample
            (should be length M)

    Outputs:
        spikeshapesup: An Nx(M*UPSAMPLEFACTOR)xD matrix with the upsampled
            spikeshapes. N is the number of spikes, M*UPSAMPLEFACTOR is the number
            of samples for each spike, and D is the number of dimensions. N, M, and D
            are unchanged from the input SPIKESHAPES.
        tup: If T is given, TUP is the upscaled time values for each spike.
    """
    spikeshapes = np.array(spikeshapes)

    # Handle dimensions
    if spikeshapes.ndim == 2:
        spikeshapes = spikeshapes[:, :, np.newaxis]

    N, M, D = spikeshapes.shape

    tup = None

    # MATLAB: linspace(1, M, M*upsamplefactor)
    # MATLAB linspace includes endpoint.
    x_old = np.arange(1, M + 1)
    x_new = np.linspace(1, M, M * upsamplefactor)

    if t is not None:
        t = np.array(t)
        # Tup = interp1(1:M, t, linspace(1,M,M*upsamplefactor));
        # Default interp1 is linear.
        # But wait, description says "using spline interpolation".
        # But code uses `interp1` without method argument, which defaults to 'linear' in MATLAB.
        # Wait, usually `interp1` default is linear. `spline` function is for spline.
        # But the docstring says "using spline interpolation".
        # Let's check the code I saw:
        # `spikeshapesup = interp1(1:M, permute(spikeshapes,[2 1 3]), linspace(1,M,M*upsamplefactor));`
        # No method specified -> Linear interpolation.
        # I should probably stick to linear if code says so, even if docstring says spline.
        # Or maybe check if `vlt.signal.oversample` (mentioned in docstring) does spline?
        # But the code calls `interp1` directly.
        # I will use linear interpolation to match the code logic.

        f_t = interp1d(x_old, t, kind='linear')
        tup = f_t(x_new)

    # Interpolate spikes
    # MATLAB: interp1(1:M, permute(spikeshapes,[2 1 3]), ...)
    # permute(spikeshapes, [2 1 3]) -> M x N x D.
    # interp1 works on columns of first dimension (M).
    # result is (M*upsample) x N x D.
    # Then permute back -> N x (M*upsample) x D.

    # scipy interp1d works on last axis by default or axis argument.
    # We want to interpolate along axis 1 (M).
    # interp1d(x, y, axis=...)

    f_spikes = interp1d(x_old, spikeshapes, kind='linear', axis=1)
    spikeshapesup = f_spikes(x_new)

    return spikeshapesup, tup
