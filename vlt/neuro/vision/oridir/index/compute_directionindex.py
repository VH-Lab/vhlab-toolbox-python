import numpy as np

def compute_directionindex(angles, rates):
    """
    vlt.neuro.vision.oridir.index.compute_directionindex
    DI = vlt.neuro.vision.oridir.index.compute_directionindex( ANGLES, RATES )

    Takes ANGLES in degrees

    di = (maxrate - rate(stimulus in oppositedirection))/maxrate
           di == 1 means maximally selective
           di == 0 means not selective
    """
    angles = np.array(angles).flatten()
    rates = np.array(rates).flatten()

    ind = np.argmax(rates)
    ang = angles[ind]

    def get_rate_at_angle(target_angle):
        diffs = np.abs(angles - target_angle)
        idx = np.argmin(diffs)
        return rates[idx]

    m1 = rates[ind]
    m2 = get_rate_at_angle((ang + 180) % 360)

    di = (m1 - m2) / (m1 + 0.0001)

    return np.round(100 * di) / 100
