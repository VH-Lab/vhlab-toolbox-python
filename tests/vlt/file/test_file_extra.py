import unittest
import os
import vlt.file

class TestFileExtra(unittest.TestCase):
    def setUp(self):
        self.dirname = 'test_dir'
        self.filename = os.path.join(self.dirname, 'test.txt')
        self.lockfile = 'test_lock.txt'

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)
        if os.path.exists(self.dirname):
            os.rmdir(self.dirname)
        if os.path.exists(self.lockfile):
            os.remove(self.lockfile)

    def test_createpath(self):
        # Ensure dir does not exist
        if os.path.exists(self.dirname):
            os.rmdir(self.dirname)

        b, err = vlt.file.createpath(self.filename)
        self.assertTrue(b)
        self.assertTrue(os.path.exists(self.dirname))

    def test_checkout_lock_file(self):
        fid, key = vlt.file.checkout_lock_file(self.lockfile)
        self.assertEqual(fid, 1)
        self.assertTrue(os.path.exists(self.lockfile))
        self.assertTrue(len(key) > 0)

        # Release
        vlt.file.release_lock_file(self.lockfile, key)
        self.assertFalse(os.path.exists(self.lockfile))
