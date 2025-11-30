import unittest
import os
import shutil
import tempfile
from unittest.mock import patch

from vlt.matlab.isa_text import isa_text
from vlt.matlab.mfiledirinfo import mfiledirinfo
from vlt.matlab.findfunctionusedir import findfunctionusedir
from vlt.matlab.replacefunction import replacefunction

class TestMatlab(unittest.TestCase):
    def test_isa_text(self):
        # Python classes
        b, mro = isa_text('int', 'int')
        self.assertTrue(b)
        self.assertIn('int', mro)

        b, mro = isa_text('bool', 'int')
        self.assertTrue(b)
        self.assertIn('int', mro)

        b, mro = isa_text('int', 'str')
        self.assertFalse(b)

        # Test nonexistent class
        b, mro = isa_text('NonExistent', 'int')
        self.assertFalse(b)

        # Test string equality fallback
        b, mro = isa_text('MyClass', 'MyClass')
        self.assertTrue(b)

    def test_mfiledirinfo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create dummy .m file
            p1 = os.path.join(tmpdir, 'test1.m')
            with open(p1, 'w') as f:
                f.write('function y = test1(x)\n')

            # Create subdir
            sub = os.path.join(tmpdir, 'subdir')
            os.mkdir(sub)
            p2 = os.path.join(sub, 'test2.m')
            with open(p2, 'w') as f:
                f.write('function test2()\n')

            minfo = mfiledirinfo(tmpdir)

            # Should find 2 files
            self.assertEqual(len(minfo), 2)
            names = sorted([m['name'] for m in minfo])
            self.assertEqual(names, ['test1', 'test2'])

            # Test IgnorePackages (mock structure)
            pkg = os.path.join(tmpdir, '+pkg')
            os.mkdir(pkg)
            p3 = os.path.join(pkg, 'test3.m')
            with open(p3, 'w') as f:
                f.write('function test3\n')

            minfo = mfiledirinfo(tmpdir, IgnorePackages=1)
            self.assertEqual(len(minfo), 2) # Should ignore test3

            minfo = mfiledirinfo(tmpdir, IgnorePackages=0)
            self.assertEqual(len(minfo), 3)

    def test_findfunctionusedir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p1 = os.path.join(tmpdir, 'caller.m')
            with open(p1, 'w') as f:
                f.write('y = myfunc(x);\n')

            minfo = {'name': 'myfunc'}
            fuse = findfunctionusedir(tmpdir, minfo)

            self.assertEqual(len(fuse), 1)
            self.assertEqual(fuse[0]['name'], 'myfunc')
            self.assertEqual(fuse[0]['fullfilename'], p1)

    @patch('builtins.input', side_effect=['y']) # Mock input to say 'y'
    def test_replacefunction(self, mock_input):
        with tempfile.TemporaryDirectory() as tmpdir:
            p1 = os.path.join(tmpdir, 'caller.m')
            with open(p1, 'w') as f:
                f.write('\n\n\ny = myfunc(x);\n') # Ensure line number > 2

            # Line 4
            fuse = [{'fullfilename': p1, 'name': 'myfunc', 'line': 4, 'character': 5}]
            replacement_table = {'original': 'myfunc', 'replacement': 'newfunc'}

            # Disable=0 to allow write
            status = replacefunction(fuse, replacement_table, Disable=0)

            self.assertEqual(status[0], 'Replaced')

            # Verify file content
            with open(p1, 'r') as f:
                content = f.read()
            self.assertEqual(content, '\n\n\ny = newfunc(x);\n')

if __name__ == '__main__':
    unittest.main()
