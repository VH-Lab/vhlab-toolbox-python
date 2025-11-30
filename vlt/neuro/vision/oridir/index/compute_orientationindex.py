import numpy as np

def compute_orientationindex(angles, rates):
    """
    vlt.neuro.vision.oridir.index.compute_orientationindex
    DI = vlt.neuro.vision.oridir.index.compute_orientationindex( ANGLES, RATES )

    Takes ANGLES in degrees

    oi = (max + max_180 - max_90 - max_270)/(max)

    no interpolation done
    """

    angles = np.array(angles).flatten()
    rates = np.array(rates).flatten()

    ind = np.argmax(rates)
    ang = angles[ind]

    # In MATLAB findclosest returns [value, index].
    # I need to check vlt.data.findclosest implementation in python.
    # It likely returns index, value or value, index.

    # Let's assume standard behavior or check it.
    # Memory doesn't say. I'll read it.

    # Assuming standard signature: index, value = findclosest(array, val) or similar?
    # MATLAB: [value, index] = findclosest(...) if it mimics MATLAB `min`?
    # No, usually custom function.

    # I will create a temporary plan to check findclosest.

    # For now I will assume it returns (index, value) or similar and adjust later.
    # But I can't write invalid code.

    # Let's peek at findclosest.py.
    # If I can't, I'll assume it returns index.

    # Wait, I can assume I need to find index of closest angle.

    def get_rate_at_angle(target_angle):
        # find index of closest angle
        diffs = np.abs(angles - target_angle)
        idx = np.argmin(diffs)
        return rates[idx]

    m1 = rates[ind] # max rate
    m2 = get_rate_at_angle((ang + 180) % 360)
    m3 = get_rate_at_angle((ang + 90) % 360)
    m4 = get_rate_at_angle((ang + 270) % 360)

    di = (m1 - m2) / (m1 + 0.0001)
    oi = (m1 + m2 - m3 - m4) / (0.0001 + (m1 + m2))

    # di = round(100*di)/100;
    # oi = round(100*oi)/100;

    return np.round(100 * oi) / 100
