import numpy as np

def point2samplelabel(ti, dt, t0=0):
    """
    Convert a continuous point to a sample number for regularly sampled data.

    s = point2samplelabel(ti, dt, t0=0)

    Given an array of time values ti, returns the closest sample
    for a signal that is regularly sampled at interval dt.
    The closest sample number is determined by rounding.
    Samples are assumed to be numbered as s = t0 + n*dt (Notice that
    these sample labels can be negative or 0).

    t0 is the time of the first sample of the signal. If t0 is not
    provided, it is assumed to be 0.

    Returns 1-based sample index to match MATLAB behavior if requested, but
    usually in Python we might want 0-based.
    However, the MATLAB code returns `s = 1 + round((ti-t0)/dt)`.
    So s=1 corresponds to ti=t0.

    We should probably stick to what the MATLAB function does which is returning a number.
    It seems `s` is used as an index in some places but as a label in others.

    In `vhsb_read`, `s` is used to calculate offset: `fseek(fo,h.sample_size*(s(1)-1),'cof');`
    So if s=1, offset is 0. This implies s is 1-based index.

    So we will return `1 + round((ti-t0)/dt)`.
    """
    ti = np.array(ti)
    return 1 + np.round((ti - t0) / dt).astype(int)
