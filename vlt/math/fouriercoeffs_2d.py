import numpy as np


def fouriercoeffs_2d(X, pixelsize):
    """
    FOURIERCOEFFS_2D - calculate Fourier coeffients for 2-d fourier analysis

    Y, FX, FY, R, FR = vlt.math.fouriercoeffs_2d(X, pixelsize)

    Given a 2-dimensional signal X (such as an image) and the pixel size in meters (PIXELSIZE), then
    the following are computed:

     Y = shifted discrete 2d fourier transform of X (shifted with fftshift)
         These coefficients are normalized so that a*exp(-sqrt(-1)*2*pi*n/T)) has coefficient of a
         This differs from the default normalization (none) of the discrete 2d fourier transform
     FX - the frequencies examined in the second dimension (columns) (shifted, so negative
          frequencies come first and zero frequency is at the center)
     FY - the frequencies examined in the first dimension (rows) (shifted)
     R - the Fourier cofficients at fixed radii (averaged over one half-plane, since
         the other half holds the complex conjugates for real X)
     FR - the Fourier frequencies at fixed radii

    Example:
        import numpy as np
        import vlt.math
        x = np.arange(1000) * 0.001  # 1 mm steps to 1 meter (don't repeat the sample at 1 meter)
        X1, X2 = np.meshgrid(x, x)
        X = 1 + 0.5 * np.sin(2 * np.pi * 3 * X1)  # a grating at 3 cycles per meter
        Y, FX, FY, R, FR = vlt.math.fouriercoeffs_2d(X, 0.001)
        # abs(R) peaks at FR == 3 with magnitude 0.5
    """
    X = np.asarray(X)
    M, N = X.shape

    # bins at or above ceil(n/2) are negative frequencies, so fftshift puts them first
    FX, FY = np.meshgrid(np.fft.fftfreq(N, d=pixelsize), np.fft.fftfreq(M, d=pixelsize))
    FX = np.fft.fftshift(FX)
    FY = np.fft.fftshift(FY)

    Y_ = 2 * np.fft.fft2(X) / (M * N)  # use factor of 2 to normalize so coefficient of a * sin(2*pi*t+t0) is a rather than a/2
    Y_[0, 0] = Y_[0, 0] / 2  # but don't do this for the DC component
    Y = np.fft.fftshift(Y_)

    half_plane = (FX > 0) | ((FX == 0) & (FY >= 0))  # the other half holds the complex conjugates
    R2 = FX[half_plane] ** 2 + FY[half_plane] ** 2
    u, group = np.unique(R2, return_inverse=True)
    counts = np.bincount(group)
    R = (np.bincount(group, weights=Y[half_plane].real) + 1j * np.bincount(group, weights=Y[half_plane].imag)) / counts
    FR = np.sqrt(u)

    return Y, FX, FY, R, FR
