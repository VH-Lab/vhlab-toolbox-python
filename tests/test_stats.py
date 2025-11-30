import unittest
import numpy as np
from vlt.stats.stderr import stderr

class TestStderr(unittest.TestCase):
    def test_stderr_vector(self):
        data = [1, 2, 3, 4, 5]
        # std(data) = 1.5811
        # sqrt(5) = 2.2361
        # se = 1.5811 / 2.2361 = 0.7071

        se = stderr(data)
        self.assertAlmostEqual(se, 0.7071, places=4)

    def test_stderr_matrix(self):
        data = np.array([[1, 2], [3, 4], [5, 6]])
        # col 1: 1,3,5. std = 2. se = 2/sqrt(3) = 1.1547
        # col 2: 2,4,6. std = 2. se = 1.1547

        se = stderr(data)
        self.assertTrue(np.allclose(se, [1.1547, 1.1547], atol=1e-4))

if __name__ == '__main__':
    unittest.main()
