import unittest
import os
import numpy as np
import scipy.io
import h5py
import tempfile
import shutil
import vlt.file

class TestLoad2CellList(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.mat_filename = os.path.join(self.test_dir, 'test_v5.mat')
        self.v73_filename = os.path.join(self.test_dir, 'test_v73.mat')

        # Create a v5 mat file
        self.data_v5 = {
            'var1': np.array([1, 2, 3]),
            'var2': np.array([[4, 5], [6, 7]]),
            'my_str': 'hello'
        }
        scipy.io.savemat(self.mat_filename, self.data_v5)

        # Create a v7.3 mat file (using h5py manually to simulate)
        with h5py.File(self.v73_filename, 'w') as f:
            # Check if dataset exists before creating to avoid errors?
            # No, we are creating a new file in 'w' mode.
            # But in the previous run, I had duplicate create_dataset 'var3'.

            # Correcting the setup:
            if 'var3' not in f:
                f.create_dataset('var3', data=np.array([10, 20]))

            if 'var4' not in f:
                f.create_dataset('var4', data=np.array([[30, 40], [50, 60]]))

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_load_all_v5(self):
        objs, objnames = vlt.file.load2celllist(self.mat_filename)
        self.assertEqual(len(objnames), 3)
        self.assertIn('var1', objnames)
        self.assertIn('var2', objnames)
        self.assertIn('my_str', objnames)

        # Verify content
        idx = objnames.index('var1')
        np.testing.assert_array_equal(objs[idx].flatten(), self.data_v5['var1'])

    def test_load_filter_v5(self):
        objs, objnames = vlt.file.load2celllist(self.mat_filename, 'var*')
        self.assertEqual(len(objnames), 2)
        self.assertIn('var1', objnames)
        self.assertIn('var2', objnames)
        self.assertNotIn('my_str', objnames)

        objs, objnames = vlt.file.load2celllist(self.mat_filename, 'my_str')
        self.assertEqual(len(objnames), 1)
        self.assertIn('my_str', objnames)

    def test_load_v73_fallback(self):
        # This tests that it falls back to h5py if loadmat fails.
        objs, objnames = vlt.file.load2celllist(self.v73_filename)
        self.assertEqual(len(objnames), 2)
        self.assertIn('var3', objnames)
        self.assertIn('var4', objnames)

        # Verify content
        idx = objnames.index('var4')
        val = objs[idx]

        expected = np.array([[30, 40], [50, 60]]).T
        np.testing.assert_array_equal(val, expected)

    def test_filename_extension(self):
        # Pass filename without extension
        base = os.path.splitext(self.mat_filename)[0]
        objs, objnames = vlt.file.load2celllist(base)
        self.assertEqual(len(objnames), 3)

if __name__ == '__main__':
    unittest.main()
