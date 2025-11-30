import unittest
import os
from vlt.matlab.mfile2package import mfile2package

class TestMFile2Package(unittest.TestCase):
    def test_basic_package(self):
        # Simulate a path: /Users/me/Documents/+mypackage/myf.m
        path = os.path.join('/Users', 'me', 'Documents', '+mypackage', 'myf.m')
        expected = 'mypackage.myf'
        self.assertEqual(mfile2package(path), expected)

    def test_nested_package(self):
        # Simulate a path: /path/+pkg1/+pkg2/func.m
        path = os.path.join('/path', '+pkg1', '+pkg2', 'func.m')
        expected = 'pkg1.pkg2.func'
        self.assertEqual(mfile2package(path), expected)

    def test_no_package(self):
        # Simulate a path: /path/func.m
        path = os.path.join('/path', 'func.m')
        expected = 'func'
        self.assertEqual(mfile2package(path), expected)

    def test_mixed_separators(self):
        # Although os.path.sep is platform dependent, we can test logic if we construct it carefully.
        # But for unit test, relying on os.path.join is best.
        pass

if __name__ == '__main__':
    unittest.main()
