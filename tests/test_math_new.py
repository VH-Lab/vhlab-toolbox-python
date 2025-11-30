import unittest
import numpy as np
from vlt.math.group_enumeration import group_enumeration
from vlt.math.interval_add import interval_add
from vlt.math.rescale import rescale

class TestMathNew(unittest.TestCase):
    def test_group_enumeration(self):
        m = [1, 3, 1]
        n = 2
        g, max_n = group_enumeration(m, n)
        self.assertEqual(max_n, 3)
        # Expected g: [1, 2, 1] based on MATLAB example
        # In python implementation, I used 0-based internal logic but m is counts.
        # My implementation:
        # inc = 1.
        # overflow = 1.
        # digit=2 (m[2]=1). g[2]=1. val=1+1=2. digit_here=2%1=0->1. overflow=ceil(2/1)-1 = 2-1=1.
        # digit=1 (m[1]=3). g[1]=1. val=1+1=2. digit_here=2%3=2. overflow=ceil(2/3)-1 = 1-1=0.
        # digit=0 (m[0]=1). g[0]=1. overflow=0.
        # Result g=[1, 2, 1]. Correct.
        np.testing.assert_array_equal(g, [1, 2, 1])

        # Test n=1
        g, _ = group_enumeration(m, 1)
        np.testing.assert_array_equal(g, [1, 1, 1])

        # Test n=3
        g, _ = group_enumeration(m, 3)
        np.testing.assert_array_equal(g, [1, 3, 1])

        # Test max
        with self.assertRaises(ValueError):
            group_enumeration(m, 4)

    def test_interval_add(self):
        # i_out = vlt.math.interval_add([0 3],[3 6])  % yields [ 0 6]
        res = interval_add([[0, 3]], [3, 6])
        np.testing.assert_array_equal(res, [[0, 6]])

        # i_out = vlt.math.interval_add([0 2],[3 4])  % yields [ 0 2; 3 4]
        res = interval_add([[0, 2]], [3, 4])
        np.testing.assert_array_equal(res, [[0, 2], [3, 4]])

        # i_out = vlt.math.interval_add([0 10],[0 2]) % yields [ 0 10]
        res = interval_add([[0, 10]], [0, 2])
        np.testing.assert_array_equal(res, [[0, 10]])

        # Merge case
        # [0 2], [2 5] -> [0 5]
        res = interval_add([[0, 2]], [2, 5])
        np.testing.assert_array_equal(res, [[0, 5]])

        # Empty input
        res = interval_add([], [1, 2])
        np.testing.assert_array_equal(res, [[1, 2]])

    def test_rescale(self):
        # Test basic rescale
        # [0 10] -> [0 1]
        vals = [0, 5, 10]
        res = rescale(vals, [0, 10], [0, 1])
        np.testing.assert_array_equal(res, [0, 0.5, 1])

        # Test clipping
        vals = [-1, 5, 11]
        res = rescale(vals, [0, 10], [0, 1])
        np.testing.assert_array_equal(res, [0, 0.5, 1])

        # Test no clipping
        res = rescale(vals, [0, 10], [0, 1], noedge=True)
        np.testing.assert_array_equal(res, [-0.1, 0.5, 1.1])

if __name__ == '__main__':
    unittest.main()
