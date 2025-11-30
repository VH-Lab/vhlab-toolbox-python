import unittest
import os
import shutil
import time
import datetime
import vlt.file

class TestVltFile(unittest.TestCase):
    def setUp(self):
        if os.path.exists('test_file_dir'):
            shutil.rmtree('test_file_dir')
        os.makedirs('test_file_dir')

    def tearDown(self):
        if os.path.exists('test_file_dir'):
            shutil.rmtree('test_file_dir')

    def test_isfilepathroot(self):
        # Unix style
        self.assertTrue(vlt.file.isfilepathroot('/'))
        self.assertTrue(vlt.file.isfilepathroot('/home'))
        self.assertFalse(vlt.file.isfilepathroot('home'))

        # We can't easily test Windows paths on Linux/Unix environment if os.name != 'nt'
        # but the function logic checks os.name.

    def test_isfile(self):
        f = os.path.join('test_file_dir', 'test.txt')
        self.assertFalse(vlt.file.isfile(f))
        with open(f, 'w') as fh:
            fh.write('content')
        self.assertTrue(vlt.file.isfile(f))

    def test_fullfilename(self):
        f = 'test.txt'
        full = vlt.file.fullfilename(f)
        self.assertTrue(os.path.isabs(full))
        self.assertTrue(full.endswith(f))

    def test_createpath(self):
        d = os.path.join('test_file_dir', 'subdir', 'file.txt')
        b, err = vlt.file.createpath(d)
        self.assertTrue(b)
        self.assertTrue(os.path.exists(os.path.dirname(d)))

        # Test existing
        b, err = vlt.file.createpath(d)
        self.assertTrue(b)

    def test_touch(self):
        f = os.path.join('test_file_dir', 'touch.txt')
        vlt.file.touch(f)
        self.assertTrue(os.path.exists(f))

        # Touch existing
        vlt.file.touch(f)
        self.assertTrue(os.path.exists(f))

    def test_text2cellstr_cellstr2text(self):
        f = os.path.join('test_file_dir', 'list.txt')
        cs = ['line1', 'line2', 'line3']
        vlt.file.cellstr2text(f, cs)

        self.assertTrue(os.path.exists(f))

        read_cs = vlt.file.text2cellstr(f)
        self.assertEqual(cs, read_cs)

    def test_filename_value(self):
        self.assertEqual(vlt.file.filename_value('test'), 'test')

        class MockFileObj:
            def __init__(self, name):
                self.name = name
                self.read = True

        m = MockFileObj('mockfile')
        self.assertEqual(vlt.file.filename_value(m), 'mockfile')

        class MockFullpath:
            def __init__(self, path):
                self.fullpathfilename = path

        m2 = MockFullpath('fullpath')
        self.assertEqual(vlt.file.filename_value(m2), 'fullpath')

    def test_checkout_release_lock_file(self):
        f = os.path.join('test_file_dir', 'lockfile')

        # Checkout
        fid, key = vlt.file.checkout_lock_file(f, checkloops=5, expiration=1)
        self.assertEqual(fid, 1)
        self.assertTrue(os.path.exists(f))

        # Try to checkout again (should fail)
        fid2, key2 = vlt.file.checkout_lock_file(f, checkloops=2, expiration=1)
        self.assertEqual(fid2, -1)

        # Release
        res = vlt.file.release_lock_file(f, key)
        self.assertTrue(res)
        self.assertFalse(os.path.exists(f))

        # Release with wrong key
        fid, key = vlt.file.checkout_lock_file(f)
        res = vlt.file.release_lock_file(f, 'wrongkey')
        self.assertFalse(res)
        self.assertTrue(os.path.exists(f)) # Should still exist

        # Cleanup
        vlt.file.release_lock_file(f, key)

    def test_addline(self):
        f = os.path.join('test_file_dir', 'log.txt')

        b, err = vlt.file.addline(f, 'line1')
        self.assertTrue(b, err)

        b, err = vlt.file.addline(f, 'line2')
        self.assertTrue(b, err)

        lines = vlt.file.text2cellstr(f)
        self.assertEqual(lines, ['line1', 'line2'])

        # Test locking behavior implies concurrent access safety,
        # but hard to test reliably without multiprocessing.
        # Minimal check: lock file should not exist after operation
        lockfile = vlt.file.fullfilename(f) + '-lock'
        self.assertFalse(os.path.exists(lockfile))

if __name__ == '__main__':
    unittest.main()
