import unittest
from vlt.path.absolute2relative import absolute2relative

class TestAbsolute2Relative(unittest.TestCase):
    def test_basic_example(self):
        # Example from docstring
        p1 = '/Users/me/mydir1/mydir2/myfile1.m'
        p2 = '/Users/me/mydir3/myfile2.m'
        expected = '../mydir1/mydir2/myfile1.m'

        result = absolute2relative(p1, p2)
        self.assertEqual(result, expected)

    def test_same_dir(self):
        p1 = '/a/b/file1.txt'
        p2 = '/a/b/file2.txt'
        # depth = 3 ('', 'a', 'b'). c2 len = 4. c2_depth = 3. diff = 0.
        # forward = file1.txt
        expected = 'file1.txt'
        result = absolute2relative(p1, p2)
        self.assertEqual(result, expected)

    def test_different_roots(self):
        p1 = '/a/b/file.txt'
        p2 = '/c/d/file.txt'
        # depth = 1 (''). c2 len = 4. c2_depth = 3. diff = 2.
        # ../../a/b/file.txt
        expected = '../../a/b/file.txt'
        result = absolute2relative(p1, p2)
        self.assertEqual(result, expected)

    def test_input_filesep(self):
        p1 = '\\a\\b\\file.txt'
        p2 = '\\a\\c\\file.txt'
        # Using backslash as input
        expected = '../b/file.txt'
        result = absolute2relative(p1, p2, input_filesep='\\')
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
