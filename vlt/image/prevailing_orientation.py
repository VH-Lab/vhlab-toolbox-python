import numpy as np
from scipy import ndimage


def prevailing_orientation(im):
    """
    Determine the prevailing orientation (strongest oriented sinwave signal) of an image.

    theta, im_out = prevailing_orientation(im)

    Performs a 2D Fourier transform on the image IM and identifies the prevailing image
    orientation by finding the peak non-DC sinusoidal component.

    THETA is the orientation in radians. Because the Fourier transform of a real
    image has two mirror-image peaks, THETA is an orientation (defined modulo pi):
    THETA and THETA+pi (or THETA-pi) describe the same orientation, and either may
    be returned. THETA lies in (-pi, pi].

    This function will likely work poorly on data that is not a simple sinusoid or that
    lacks a dominant sinusoid.

    IM_OUT is a version of the image rotated by THETA (counterclockwise, as displayed
    with row 0 at the top), using bilinear interpolation, keeping the size of IM and
    filling with 0 outside the image. This parallels Matlab's
    IMROTATE(IM, THETA_DEGREES, 'bilinear', 'crop'); values near the edges may differ
    slightly because the interpolation routines are not identical.

    Developer's note: this function takes the peak in the 2-d fourier space as evidence of
    the phase. This results in a small error for some low spatial frequencies. The function
    could be improved.

    Example:
        import numpy as np
        import vlt.image
        x, y = np.meshgrid(np.arange(-100, 101), np.arange(-100, 101))
        im = np.sin(0.3 * x + 0.1 * y)
        theta, im_out = vlt.image.prevailing_orientation(im)
    """
    im = np.asarray(im, dtype=float)
    Y = np.fft.fft2(im)
    m, n = im.shape

    Y[0, 0] = 0  # disallow 0 point

    A = np.abs(Y)
    bigmax = A.max()

    # select only a single point; search in column-major order to match Matlab's FIND
    idx = np.flatnonzero((A == bigmax).ravel(order='F'))[0]
    p, q = np.unravel_index(idx, A.shape, order='F')

    # fft2 is:
    # Y[p,q] = sum_{j=0}^{m-1} sum_{k=0}^{n-1} exp(-2*pi*i*j*p/m) * exp(-2*pi*i*k*q/n) * im[j,k]
    #
    # The wave vector of this component is (p/m, q/n) cycles per sample along
    # dimensions 0 and 1. The FFT indices p = 0..m-1 and q = 0..n-1 are not signed
    # frequencies, though: indices above m/2 (n/2) are aliases of the negative
    # frequencies p-m (q-n). Without wrapping them, p and q are always >= 0 and the
    # angle could only fall in [0, pi/2]. So we wrap p and q to signed frequencies
    # and take the angle of the wave vector:
    #     tan(theta) = (p/m) / (q/n)
    # Because the FFT of a real image has mirror peaks at (p,q) and (-p,-q), theta is
    # only defined modulo pi.

    p = int(p)
    q = int(q)

    # wrap to signed frequencies
    if p > m / 2:
        p = p - m
    if q > n / 2:
        q = q - n

    theta = float(np.arctan2(p / m, q / n))

    theta_degrees = np.degrees(theta)

    im_out = ndimage.rotate(im, theta_degrees, reshape=False, order=1, mode='constant', cval=0.0)

    return theta, im_out
