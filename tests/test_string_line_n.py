import unittest
from vlt.string.line_n import line_n

class TestLineN(unittest.TestCase):
    def test_basic_lines(self):
        s = "Line 1\nLine 2\nLine 3"

        # Test line 1
        l, pos, marks = line_n(s, 1)
        self.assertEqual(l, "Line 1")
        self.assertEqual(pos, 1)
        # marks should be [7, 14, 21] ?
        # 'Line 1' len 6. \n at 7.
        # 'Line 2' len 6. 7+6=13. \n at 14.
        # 'Line 3' len 6. 14+6=20. No \n. Virtual mark at 21 (len+1).
        # len(s) = 20.
        self.assertEqual(marks, [7, 14, 21])

        # Test line 2
        l, pos, marks = line_n(s, 2)
        self.assertEqual(l, "Line 2")
        self.assertEqual(pos, 8)

        # Test line 3
        l, pos, marks = line_n(s, 3)
        self.assertEqual(l, "Line 3")
        self.assertEqual(pos, 15)

    def test_with_trailing_newline(self):
        s = "Line 1\n"
        l, pos, marks = line_n(s, 1)
        self.assertEqual(l, "Line 1")
        self.assertEqual(marks, [7]) # len is 7. mark at 7.

    def test_out_of_bounds(self):
        s = "Line 1"
        with self.assertRaises(ValueError):
            line_n(s, 2)
        with self.assertRaises(ValueError):
            line_n(s, 0)

    def test_empty_string(self):
        s = ""
        # Should have 1 empty line?
        # eol_marks will be [1] (len 0 + 1)
        l, pos, marks = line_n(s, 1)
        self.assertEqual(l, "")
        self.assertEqual(pos, 1)
        self.assertEqual(marks, [1])

if __name__ == '__main__':
    unittest.main()
