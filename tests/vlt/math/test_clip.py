import unittest
import vlt.math.clip

class TestClip(unittest.TestCase):
    def test_clip(self):
        a = [-float('inf'), 0, 1, 2, 3, float('inf')]
        clipvar = [1, 2]
        expected = [1, 1, 1, 2, 2, 2]
        result = vlt.math.clip(a, clipvar)
        self.assertEqual(list(result), expected)

    def test_clip_scalar(self):
        self.assertEqual(vlt.math.clip(0, [1, 2]), 1)
        self.assertEqual(vlt.math.clip(1.5, [1, 2]), 1.5)
        self.assertEqual(vlt.math.clip(3, [1, 2]), 2)
