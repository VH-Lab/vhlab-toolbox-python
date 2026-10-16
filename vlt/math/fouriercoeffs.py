import numpy as np


def fouriercoeffs(data, si):
    """
    FOURIERCOEFFS - find Fourier coefficients for data

    Uses FFT to compute the Fourier coefficients for a vector of data.

    fc, freqs = vlt.math.fouriercoeffs(data, si)

    where DATA is a vector of data and SI is the sampling interval (in seconds),
    returns FC the Fourier coefficients and FREQS, the frequency of
    each coefficient.

    The Fourier coefficients are defined [1] to be:
      B0   = (1/T) * sum(data)   (returned in fc[0])
      Bn   = (2/T) * integral(0,T,data.*cos(2*pi*n/T))  (returned in fc[n].real)
      An   = (2/T) * integral(0,T,data.*sin(2*pi*n/T))  (returned in fc[n].imag)

    Each entry of FC is the sum of Bn+An*1j so that
    Bn = fc[n].real and An = fc[n].imag

    FFT treats the N samples as one period of length N*si, so fc[n] is at
    frequency n/(N*si). Don't repeat the first sample at the end of DATA.

    Note that these Fourier cofficients are normalized differently than those returned
    by numpy.fft.fft.

    [1]: _Waves_, Berkeley Physics Course Volume 3, Crawford, 1968

    Example:
        import numpy as np
        import vlt.math
        t = np.arange(3000) * 0.001  # 3 s of data; don't repeat the sample at t=3
        s = 2 + 0.5 * np.sin(2 * np.pi * 4 * t + np.pi / 3)
        fc, freqs = vlt.math.fouriercoeffs(s, 0.001)
        # abs(fc) peaks at freqs == 4 with magnitude 0.5
    """
    data = np.asarray(data).ravel()
    n = data.size

    fc = np.fft.fft(data)
    fc[0] = fc[0] / n
    fc[1:] = (2 / n) * np.conj(fc[1:])
    freqs = np.arange(n) / (si * n)

    return fc, freqs
