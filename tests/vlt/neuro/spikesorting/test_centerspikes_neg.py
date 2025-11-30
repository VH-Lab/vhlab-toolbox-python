import unittest
import numpy as np
from vlt.neuro.spikesorting.centerspikes_neg import centerspikes_neg

class TestCenterSpikesNeg(unittest.TestCase):
    def test_centerspikes_neg(self):
        # Create a synthetic spike
        # 30 samples, peak at index 10 (0-based)
        M = 30
        spike = np.zeros(M)
        spike[10] = -1.0 # Peak

        # Center is at index 15 (if M=30, round(30/2)=15 in MATLAB -> index 14 in Python)
        # Python center_idx = int(floor(30/2 + 0.5)) - 1 = 15 - 1 = 14.
        # Peak is at 10.
        # Shift should be 10 - 14 = -4.

        # N=1, M=30, D=1
        spikes = spike.reshape(1, M, 1)
        center_range = 10

        centered, shifts = centerspikes_neg(spikes, center_range)

        # shifts[0] should be -shift = -(-4) = 4.
        # Wait, my code: shifts[i] = -shift.
        # shift = min_row - center_range.
        # search_indices = [-range ... +range] + center_idx.
        # min_idx in original spike = 10.
        # center_idx = 14.
        # shift should be -4.
        # shifts[i] should be 4.

        self.assertEqual(shifts[0], 4)

        # Check if centered spike peak is at center
        # The output `centered` is sliced to length M.
        # If we shift by -4 (move peak to center), the new peak should be at center_idx?
        # Wait, if we shift by -4.
        # We pad, then slice.
        # start_idx = shift + center_range = -4 + 10 = 6.
        # We slice padded[6 : 6+30].
        # Original spike is at padded[10:40] (center_range=10).
        # Spike peak is at 10 + 10 = 20 in padded array.
        # Sliced array starts at 6.
        # Peak index in sliced array = 20 - 6 = 14.
        # center_idx_py is 14.
        # So peak is at center. Correct.

        self.assertEqual(centered[0, 14, 0], -1.0)

    def test_centerspikes_multichannel(self):
        # N=1, M=30, D=2
        # Channel 0 has small peak, Channel 1 has large peak
        M = 30
        spike = np.zeros((M, 2))
        spike[10, 0] = -0.5
        spike[12, 1] = -1.0 # Larger negative peak at 12

        # Center is 14.
        # Peak at 12. Shift = 12 - 14 = -2.
        # Output shifts = 2.

        spikes = spike.reshape(1, M, 2)
        center_range = 10

        centered, shifts = centerspikes_neg(spikes, center_range)

        self.assertEqual(shifts[0], 2)
        # Peak of channel 1 should be at 14
        self.assertEqual(centered[0, 14, 1], -1.0)
        # Peak of channel 0 was at 10. Shifted by +2 -> 12?
        # Peak at 10. Shift is -2 (move 12 to 14).
        # So everything moves right by 2.
        # 10 -> 12.
        self.assertEqual(centered[0, 12, 0], -0.5)

if __name__ == '__main__':
    unittest.main()
