import numpy as np

def fit2fitoidiffsum(R, blank=None):
    """
    FIT2FITOIDIFFSUM
    """
    R = np.array(R)
    directions = R[0, :]
    responses = R[1, :]

    mx_idx = np.argmax(responses)
    Ot = directions[mx_idx]

    def get_index(target):
        diffs = np.abs(directions - target)
        return np.argmin(diffs)

    OtPi = get_index(Ot)
    OtNi = get_index((Ot + 180) % 360)
    OtO1i = get_index((Ot + 90) % 360)
    OtO2i = get_index((Ot - 90) % 360)

    r_pref = responses[OtPi] + responses[OtNi]
    r_orth = responses[OtO1i] + responses[OtO2i]

    denom = r_pref + r_orth
    if denom == 0: return np.nan

    return (r_pref - r_orth) / denom
