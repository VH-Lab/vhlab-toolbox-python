import unittest
import numpy as np
from vlt.neuro.spikesorting.oversamplespikes import oversamplespikes

class TestOversampleSpikes(unittest.TestCase):
    def test_oversamplespikes(self):
        # Create a simple ramp spike
        # M=10
        M = 10
        spike = np.arange(M).reshape(1, M, 1) # 0, 1, ..., 9

        upsamplefactor = 2
        # Expected M_new = 20
        # Linear interpolation from 1 to 10 onto 20 points (1 to 10).
        # np.linspace(1, 10, 20) -> 1.0, 1.47, ... 10.0

        spike_up, tup = oversamplespikes(spike, upsamplefactor)

        self.assertEqual(spike_up.shape, (1, 20, 1))
        self.assertAlmostEqual(spike_up[0, 0, 0], 0.0) # Start
        self.assertAlmostEqual(spike_up[0, -1, 0], 9.0) # End

        # Check midpoint
        # Original indices: 0..9.
        # New indices: 0..19.
        # x_old = 1..10. x_new = linspace(1, 10, 20).
        # x_new[1] should be 1 + (9/19).
        # spike[1] corresponds to x=2 (value 1).
        # Let's check a known point.
        # If we interpolate linearly, intermediate values should follow the line y = x-1.

        x_new = np.linspace(1, M, M * upsamplefactor)
        expected = x_new - 1

        np.testing.assert_allclose(spike_up[0, :, 0], expected)

    def test_with_time(self):
        M = 5
        spike = np.zeros((1, M, 1))
        t = np.array([0, 10, 20, 30, 40])
        upsamplefactor = 2

        spike_up, tup = oversamplespikes(spike, upsamplefactor, t=t)

        self.assertEqual(len(tup), 10)
        self.assertAlmostEqual(tup[0], 0)
        self.assertAlmostEqual(tup[-1], 40)

        # Linear interpolation of time
        # 1..5 mapped to 1..5 on 10 points.
        # t is linear, so tup should be linear from 0 to 40.
        expected_t = np.linspace(0, 40, 10)
        np.testing.assert_allclose(tup, expected_t)

if __name__ == '__main__':
    unittest.main()
