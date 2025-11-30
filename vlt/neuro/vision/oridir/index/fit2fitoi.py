import numpy as np

def fit2fitoi(R, blank=None):
    """
    FIT2FITOI - Calculate orientation index from a double gaussian fit of direction tuning curve

    OIIND = vlt.neuro.vision.oridir.index.fit2fitoi(R)

    R is a 2-row vector (or 2xN array).
    row 0: directions
    row 1: responses
    """

    R = np.array(R)
    directions = R[0, :]
    responses = R[1, :]

    mx_idx = np.argmax(responses)
    Ot = directions[mx_idx]

    # In MATLAB findclosest returns [value, index] (actually likely [index, value] or [value, index], I need to check usage)
    # Looking at `compute_tuningwidth`, `vlt.data.findclosest(intrates(pref-90:pref),halfheight)` returns `[left, leftvalue]`.
    # Usually `min` returns `[val, idx]`.
    # `findclosest` likely mimics that: `[val, idx] = min(abs(x-val))`.
    # So `OtPi = vlt.data.findclosest(directions,Ot)` returns `val, idx`?
    # Wait, `R(OtPi)`. If `OtPi` is used as index, it must be the index.
    # In MATLAB `[val, idx] = min(...)`.
    # If `findclosest` returns `[val, idx]`, then `OtPi` would be `val`.
    # But `R(OtPi)` implies `OtPi` is index.
    # Maybe `findclosest` returns `[idx, val]`?
    # Or maybe `OtPi` is the second return value?
    # MATLAB: `OtPi = vlt.data.findclosest(...)`. If it returns 2 values, it assigns first to OtPi.
    # So OtPi is the first return value.
    # If OtPi is used as index, then `findclosest` must return index as first value.

    # Let's check `vlt/data/findclosest.py`.

    # Assume findclosest returns index first.

    def get_index(target):
        diffs = np.abs(directions - target)
        return np.argmin(diffs)

    OtPi = get_index(Ot)
    OtNi = get_index((Ot + 180) % 360)
    OtO1i = get_index((Ot + 90) % 360)
    OtO2i = get_index((Ot - 90) % 360)

    r_pref = responses[OtPi] + responses[OtNi]
    r_orth = responses[OtO1i] + responses[OtO2i]

    if r_pref == 0:
        return np.nan # Avoid division by zero

    oiindfit = (r_pref - r_orth) / r_pref

    return oiindfit
