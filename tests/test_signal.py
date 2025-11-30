import unittest
import numpy as np
from vlt.signal.dotdisc import dotdisc
from vlt.signal.refractory import refractory
from vlt.signal.value2sample import value2sample

class TestDotDisc(unittest.TestCase):
    def test_dotdisc_simple(self):
        # Create a simple signal with a peak
        data = np.zeros(20)
        data[10] = 10 # Peak

        # Dot 1: Threshold 5, Sign 1, Offset 0. (Val > 5)
        dots = [[5, 1, 0]]

        events = dotdisc(data, dots)
        # Expect index 10 to pass
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0], 10)

    def test_dotdisc_adjacent(self):
        # Signal with adjacent passing points
        data = np.zeros(20)
        data[9] = 6
        data[10] = 10
        data[11] = 6

        # Dot 1: Threshold 5, Sign 1, Offset 0.
        dots = [[5, 1, 0]]

        events = dotdisc(data, dots)
        # Indices 9, 10, 11 pass. Mean is 10.
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0], 10)

    def test_dotdisc_multiple_dots(self):
        # Signal where a peak must be followed by a dip
        data = np.zeros(20)
        data[10] = 10
        data[12] = -5

        # Dot 1: Thresh 5, Sign 1, Offset 0 (Peak > 5 at i)
        # Dot 2: Thresh 2, Sign -1, Offset 2 (Value < -2 at i+2) => data[i+2] * -1 > 2 => data[i+2] < -2
        dots = [
            [5, 1, 0],
            [2, -1, 2]
        ]

        events = dotdisc(data, dots)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0], 10)

        # Test failure case
        dots_fail = [
            [5, 1, 0],
            [10, -1, 2] # Require < -10 at i+2, but we have -5
        ]
        events_fail = dotdisc(data, dots_fail)
        self.assertEqual(len(events_fail), 0)

    def test_dotdisc_negative_offset(self):
        # Signal where peak is PRECEDED by a value
        data = np.zeros(20)
        data[10] = 10
        data[8] = -5

        # Dot 1: Thresh 5, Sign 1, Offset 0 (Peak at i)
        # Dot 2: Thresh 2, Sign -1, Offset -2 (Value < -2 at i-2)
        dots = [
            [5, 1, 0],
            [2, -1, -2]
        ]

        events = dotdisc(data, dots)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0], 10)

        # Verify that mask bug doesn't exclude valid points
        # If I had the bug: check_vals[:-2] = False.
        # This would clear indices 0 to 17. Index 10 would be cleared!
        # So it would return empty.

        # Verify boundary condition for negative offset
        # If peak is at 1, offset -2 means looking at -1 (wrap). Should be excluded.
        data2 = np.zeros(20)
        data2[1] = 10
        # data2[-1] = -5 # Wrap around pos
        # Even if we have -5 at end, it shouldn't count because of boundary check.
        data2[19] = -5

        events2 = dotdisc(data2, dots)
        self.assertEqual(len(events2), 0)


class TestRefractory(unittest.TestCase):
    def test_refractory(self):
        # Test 1: Simple case
        in_times = [1, 1.5, 3, 4, 4.2]
        ref = 1.0

        out_times, out_inds = refractory(in_times, ref)
        np.testing.assert_array_equal(out_times, [1, 3])
        np.testing.assert_array_equal(out_inds, [0, 2])

        # Test 2: Unsorted input
        in_times = [4.2, 1, 3, 1.5, 4] # same as above but scrambled

        out_times, out_inds = refractory(in_times, ref)
        np.testing.assert_array_equal(out_times, [1, 3])
        np.testing.assert_array_equal(out_inds, [1, 2])

class TestValue2Sample(unittest.TestCase):
    def test_value2sample(self):
        # Example from doc: s = vlt.signal.value2sample(1, 1000, 0) % s is 1001
        s = value2sample(1, 1000, 0)
        self.assertEqual(s, 1001)

        # Test array
        v = [0, 1]
        s = value2sample(v, 1000, 0)
        np.testing.assert_array_equal(s, [1, 1001])

if __name__ == '__main__':
    unittest.main()
