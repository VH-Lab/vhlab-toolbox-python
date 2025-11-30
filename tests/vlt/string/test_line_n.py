import unittest
import vlt.string.line_n

class TestLineN(unittest.TestCase):
    def test_line_n(self):
        s = "Line 1\nLine 2\nLine 3"

        l1, p1, e1 = vlt.string.line_n(s, 1)
        self.assertEqual(l1, "Line 1")
        self.assertEqual(p1, 1)

        l2, p2, e2 = vlt.string.line_n(s, 2)
        self.assertEqual(l2, "Line 2")
        self.assertEqual(p2, 8) # 1-based: "Line 1\n" is 7 chars. So 8.

        l3, p3, e3 = vlt.string.line_n(s, 3)
        self.assertEqual(l3, "Line 3")

    def test_line_n_trailing_newline(self):
        s = "L1\nL2\n"
        l1, _, _ = vlt.string.line_n(s, 1)
        self.assertEqual(l1, "L1")
        l2, _, _ = vlt.string.line_n(s, 2)
        self.assertEqual(l2, "L2")

    def test_line_n_out_of_bounds(self):
        s = "L1"
        with self.assertRaises(Exception):
            vlt.string.line_n(s, 2)
