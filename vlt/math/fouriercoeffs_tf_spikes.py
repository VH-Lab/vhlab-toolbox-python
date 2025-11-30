import numpy as np

def fouriercoeffs_tf_spikes(spiketimes, tf, duration):
    """
    FOURIERCOEFFS_TF_SPIKES  Fourier Transform of a spike train at a particular frequency.

    F = vlt.math.fouriercoeffs_tf_spikes(SPIKETIMES, TF, DURATION)

    This function returns the normalized fourier coefficient of
    a spike train that is defined by an array of SPIKETIMES with a
    duration DURATION.

    The function calculates (2/DURATION) * exp(-2*pi*sqrt(-1)*tf).
    If tf is zero it returns the number of spikes times divided by the duration.
    """

    spiketimes = np.array(spiketimes).flatten()

    if tf == 0:
        f = len(spiketimes) / duration
    else:
        # MATLAB: f = sum(exp(-2*pi*sqrt(-1)*tf*spiketimes)) * (2/duration);
        f = np.sum(np.exp(-2 * np.pi * 1j * tf * spiketimes)) * (2 / duration)

    return f
