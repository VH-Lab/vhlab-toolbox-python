import unittest

import numpy as np

import vlt.image


def _grating(phi_degrees):
    # x = columns (axis 1), y = rows (axis 0)
    x, y = np.meshgrid(np.arange(-50, 51), np.arange(-50, 51))
    phi = np.radians(phi_degrees)
    return np.sin(0.3 * (np.cos(phi) * x + np.sin(phi) * y))


class TestPrevailingOrientation(unittest.TestCase):
    PHI_DEGREES = [0, 20, 45, 70, 90, 120, 160]

    def test_theta_matches_orientation(self):
        for phi_degrees in self.PHI_DEGREES:
            with self.subTest(phi_degrees=phi_degrees):
                theta, _ = vlt.image.prevailing_orientation(_grating(phi_degrees))
                self.assertGreater(theta, -np.pi)
                self.assertLessEqual(theta, np.pi)
                # theta is an orientation, so compare modulo pi
                angle_diff = (theta - np.radians(phi_degrees) + np.pi / 2) % np.pi - np.pi / 2
                self.assertLess(abs(angle_diff), np.radians(5))

    def test_rotation_aligns_grating(self):
        for phi_degrees in self.PHI_DEGREES:
            with self.subTest(phi_degrees=phi_degrees):
                _, im_out = vlt.image.prevailing_orientation(_grating(phi_degrees))
                center = 50
                half_width = 15
                crop = im_out[center - half_width:center + half_width + 1,
                              center - half_width:center + half_width + 1]
                var_along_dim0 = np.mean(np.var(crop, axis=0, ddof=1))
                var_along_dim1 = np.mean(np.var(crop, axis=1, ddof=1))
                self.assertLess(var_along_dim0, 0.1)
                self.assertGreater(var_along_dim1, 0.3)

    def test_matches_matlab_theta_values(self):
        # values from the Matlab vlt.image.prevailing_orientation on the same gratings
        expected_degrees = {0: 0.0, 20: 21.8, 45: 45.0, 70: 68.2, 90: 90.0}
        for phi_degrees, expected in expected_degrees.items():
            with self.subTest(phi_degrees=phi_degrees):
                theta, _ = vlt.image.prevailing_orientation(_grating(phi_degrees))
                self.assertAlmostEqual(np.degrees(theta), expected, places=1)

    def test_output_shape(self):
        im = _grating(30)[:80, :]
        theta, im_out = vlt.image.prevailing_orientation(im)
        self.assertEqual(im_out.shape, im.shape)
        self.assertIsInstance(theta, float)


if __name__ == '__main__':
    unittest.main()
