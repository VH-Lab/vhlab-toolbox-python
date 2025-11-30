import numpy as np

def samplelabel2point(s, dt, t0=0):
    """
    Convert a sample number to a continuous point for regularly sampled data.

    ti = samplelabel2point(s, dt, t0=0)

    Inverse of point2samplelabel.
    s = 1 + round((ti-t0)/dt) => s-1 = (ti-t0)/dt => ti = t0 + (s-1)*dt
    """
    s = np.array(s)
    return t0 + (s - 1) * dt
