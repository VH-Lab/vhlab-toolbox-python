import unittest
import os
from vlt.file.text2cellstr import text2cellstr

class TestText2CellStr(unittest.TestCase):
    def setUp(self):
        self.filename = 'temp_text2cellstr.txt'
        with open(self.filename, 'w') as f:
            f.write("Line 1\nLine 2\nLine 3")

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_read_lines(self):
        c = text2cellstr(self.filename)
        self.assertEqual(c, ["Line 1", "Line 2", "Line 3"])

    def test_trailing_newline(self):
        with open(self.filename, 'w') as f:
            f.write("Line 1\n")
        c = text2cellstr(self.filename)
        self.assertEqual(c, ["Line 1"])
        # Note: if there is a trailing newline, splitlines or typical editors usually show 1 line.
        # But if we strictly follow fgetl, let's see.
        # fgetl reads up to newline.
        # "Line 1\n" -> fgetl returns "Line 1". Next call hits eof?
        # Yes.

    def test_empty_file(self):
        with open(self.filename, 'w') as f:
            pass
        c = text2cellstr(self.filename)
        self.assertEqual(c, [])

    def test_error(self):
        with self.assertRaises(IOError):
            text2cellstr("nonexistent_file.txt")

if __name__ == '__main__':
    unittest.main()
