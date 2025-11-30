import numpy as np

def compute_dircircularvariance(angles, rates):
    """
    vlt.neuro.vision.oridir.index.compute_dircircularvariance
    CV = vlt.neuro.vision.oridir.index.compute_dircircularvariance( ANGLES, RATES )

    Takes ANGLES in degrees. ANGLES and RATES should be
    row vectors.

    CV = 1 - |R|
    R = (RATES * EXP(I*ANGLES)') / SUM(RATES)

    See Ringach et al. J.Neurosci. 2002 22:5639-5651
    """
    angles = np.array(angles).flatten()
    rates = np.array(rates).flatten()

    angles_rad = angles / 360 * 2 * np.pi

    # r = (rates * exp(i*angles)') / sum(abs(rates));
    r = np.dot(rates, np.exp(1j * angles_rad)) / np.sum(np.abs(rates))

    cv = 1 - np.abs(r)
    cv = np.round(100 * cv) / 100

    return cv
