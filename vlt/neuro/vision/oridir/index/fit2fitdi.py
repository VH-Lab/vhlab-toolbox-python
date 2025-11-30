import numpy as np

def fit2fitdi(R, blank=None):
    """
    FIT2FITDI
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

    r_pref = responses[OtPi]
    r_null = responses[OtNi]

    if r_pref == 0: return np.nan

    return (r_pref - r_null) / r_pref
