import unittest

import numpy as np

import vlt.math


class TestFouriercoeffs(unittest.TestCase):
    # FFT treats N samples as one period of length N*si, so bin n (0-based)
    # is at frequency n/(N*si).

    def test_peak_frequency(self):
        t = np.arange(100) / 100
        data = np.cos(2 * np.pi * 5 * t)
        fc, freqs = vlt.math.fouriercoeffs(data, 0.01)
        peak = np.argmax(np.abs(fc[:50]))
        self.assertEqual(peak, 5)
        self.assertAlmostEqual(freqs[peak], 5, places=10)
        self.assertAlmostEqual(abs(fc[peak]), 1, places=10)

    def test_frequency_spacing(self):
        si = 0.001
        N = 3000
        fc, freqs = vlt.math.fouriercoeffs(np.random.rand(N), si)
        self.assertEqual(freqs.size, N)
        self.assertEqual(freqs[0], 0)
        self.assertAlmostEqual(freqs[1], 1 / (N * si), places=10)
        np.testing.assert_allclose(np.diff(freqs), 1 / (N * si), atol=1e-9)

    def test_coefficients(self):
        # B0 = mean; Bn = cosine amplitude in real part; An = sine amplitude in imag part
        t = np.arange(1000) * 0.001
        data = 2 + 0.75 * np.cos(2 * np.pi * 3 * t) + 0.25 * np.sin(2 * np.pi * 7 * t)
        fc, freqs = vlt.math.fouriercoeffs(data, 0.001)
        self.assertAlmostEqual(fc[0].real, 2, places=10)
        self.assertAlmostEqual(fc[3].real, 0.75, places=10)
        self.assertAlmostEqual(fc[3].imag, 0, places=10)
        self.assertAlmostEqual(fc[7].real, 0, places=10)
        self.assertAlmostEqual(fc[7].imag, 0.25, places=10)


class TestFouriercoeffs2d(unittest.TestCase):

    def test_frequency_axes(self):
        # even number of rows, odd number of columns
        pixelsize = 0.01
        M, N = 8, 5
        Y, FX, FY, R, FR = vlt.math.fouriercoeffs_2d(np.random.rand(M, N), pixelsize)
        np.testing.assert_allclose(FX[0, :], np.arange(-2, 3) / (N * pixelsize), atol=1e-10)
        np.testing.assert_allclose(FY[:, 0], np.arange(-4, 4) / (M * pixelsize), atol=1e-10)

    def test_peak_frequency(self):
        pixelsize = 0.001
        x = np.arange(1000) * pixelsize  # 1 meter, without repeating the endpoint
        X1, X2 = np.meshgrid(x, x)
        X = 1 + 0.5 * np.sin(2 * np.pi * 3 * X1)
        Y, FX, FY, R, FR = vlt.math.fouriercoeffs_2d(X, pixelsize)
        nondc = ~((FX == 0) & (FY == 0))
        peak = np.argmax(np.abs(Y) * nondc)
        self.assertAlmostEqual(abs(FX.flat[peak]), 3, places=10)
        self.assertAlmostEqual(FY.flat[peak], 0, places=10)
        self.assertAlmostEqual(abs(Y.flat[peak]), 0.5, places=10)
        self.assertAlmostEqual(Y[(FX == 0) & (FY == 0)][0].real, 1, places=10)

    def test_radial_average(self):
        pixelsize = 0.001
        x = np.arange(64) * pixelsize
        X1, X2 = np.meshgrid(x, x)
        f = 1 / (64 * pixelsize)  # one cycle across the image
        X = 1 + 0.5 * np.sin(2 * np.pi * 3 * f * X1)
        Y, FX, FY, R, FR = vlt.math.fouriercoeffs_2d(X, pixelsize)
        self.assertTrue(np.all(np.diff(FR) > 0))
        self.assertAlmostEqual(FR[0], 0)
        self.assertAlmostEqual(R[0].real, 1, places=10)
        # only one half-plane is averaged, so the sine is not cancelled by its conjugate
        k = np.argmin(np.abs(FR - 3 * f))
        self.assertAlmostEqual(FR[k], 3 * f, places=8)
        self.assertGreater(abs(R[k]), 0.1)
        self.assertLessEqual(FR.max(), np.sqrt(2) * 0.5 / pixelsize + 1e-9)


if __name__ == '__main__':
    unittest.main()
