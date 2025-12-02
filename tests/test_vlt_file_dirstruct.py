import unittest
import os
import shutil
import tempfile
import numpy as np
import vlt.file
from vlt.file.dirstruct import dirstruct

class TestDirstruct(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.exp_dir = os.path.join(self.test_dir, 'experiment')
        os.makedirs(self.exp_dir)

        # Create a few test directories with reference.txt
        self.t1 = os.path.join(self.exp_dir, 't00001')
        os.makedirs(self.t1)
        with open(os.path.join(self.t1, 'reference.txt'), 'w') as f:
            f.write("name\tref\ttype\n")
            f.write("TestName\t1\tTestType\n")

        self.t2 = os.path.join(self.exp_dir, 't00002')
        os.makedirs(self.t2)
        with open(os.path.join(self.t2, 'reference.txt'), 'w') as f:
            f.write("name\tref\ttype\n")
            f.write("TestName\t2\tTestType\n")

        self.t3 = os.path.join(self.exp_dir, 't00003')
        os.makedirs(self.t3)
        # Empty reference.txt
        with open(os.path.join(self.t3, 'reference.txt'), 'w') as f:
             f.write("name\tref\ttype\n")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_constructor(self):
        ds = dirstruct(self.exp_dir)
        self.assertEqual(ds.getpathname(), vlt.file.fixpath(self.exp_dir))
        self.assertTrue('t00001' in ds.getalltests())
        self.assertTrue('t00002' in ds.getalltests())
        self.assertTrue('t00003' in ds.getalltests()) # t00003 has empty ref but exists

    def test_nameref_management(self):
        ds = dirstruct(self.exp_dir)

        # Check all namerefs
        nrs = ds.getallnamerefs()
        self.assertEqual(len(nrs), 2) # t00003 has no entries
        names = [n['name'] for n in nrs]
        self.assertTrue('TestName' in names)

        # Check gettests
        tests = ds.gettests('TestName', 1)
        self.assertEqual(tests, ['t00001'])
        tests = ds.gettests('TestName', 2)
        self.assertEqual(tests, ['t00002'])

        # Check getnamerefs
        refs = ds.getnamerefs('t00001')
        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0]['name'], 'TestName')
        self.assertEqual(refs[0]['ref'], 1)

    def test_active_dirs(self):
        ds = dirstruct(self.exp_dir)
        active = ds.getactive()
        self.assertEqual(len(active), 3)

        ds.setactive(['t00001'])
        self.assertEqual(ds.getactive(), ['t00001'])
        self.assertTrue(ds.isactive('t00001'))
        self.assertFalse(ds.isactive('t00002'))

        ds.setactive(['t00002'], append=True)
        active = ds.getactive()
        self.assertTrue('t00001' in active)
        self.assertTrue('t00002' in active)

    def test_tag_management(self):
        ds = dirstruct(self.exp_dir)

        # Add tag
        ds.addtag('t00001', 'mytag', 'myvalue')

        # Check tag
        self.assertTrue(ds.hastag('t00001', 'mytag'))
        self.assertEqual(ds.gettagvalue('t00001', 'mytag'), 'myvalue')

        tags = ds.gettag('t00001')
        self.assertEqual(len(tags), 1)
        self.assertEqual(tags[0]['tagname'], 'mytag')

        # Modify tag
        ds.addtag('t00001', 'mytag', 'newvalue')
        self.assertEqual(ds.gettagvalue('t00001', 'mytag'), 'newvalue')

        # Remove tag
        ds.removetag('t00001', 'mytag')
        self.assertFalse(ds.hastag('t00001', 'mytag'))

    def test_neuter(self):
        ds = dirstruct(self.exp_dir)
        ds.neuter('t00003')

        # t00003 should no longer be in the list because reference.txt is gone (renamed)
        # dirstruct re-initializes itself in neuter.

        self.assertFalse('t00003' in ds.getalltests())

        # Check file system
        self.assertTrue(os.path.isfile(os.path.join(self.t3, 'reference0.txt')))
        self.assertFalse(os.path.isfile(os.path.join(self.t3, 'reference.txt')))

    def test_newtestdir(self):
        ds = dirstruct(self.exp_dir)
        newdir = ds.newtestdir()
        self.assertEqual(newdir, 't00004') # t00001, 2, 3 exist.

    def test_paths(self):
        ds = dirstruct(self.exp_dir)

        exp_file, exp_name = ds.getexperimentfile(createit=True)
        self.assertTrue(exp_file.endswith('experiment.mat'))
        self.assertTrue(os.path.isfile(exp_file))

        scratch = ds.getscratchdirectory(createit=True)
        self.assertTrue(os.path.isdir(scratch))

    def test_save_delete_expvar(self):
        ds = dirstruct(self.exp_dir)

        # Need scipy for this test to really work, but if not installed it should handle gracefully or fail if imported inside
        try:
            import scipy.io

            # Save
            ds.saveexpvar(123, 'myvar')

            # Verify file exists
            fn, _ = ds.getexperimentfile()
            self.assertTrue(os.path.isfile(fn))

            mat = scipy.io.loadmat(fn)
            self.assertEqual(mat['myvar'], 123)

            # Delete
            ds.deleteexpvar('myvar')

            mat = scipy.io.loadmat(fn)
            self.assertFalse('myvar' in mat)

        except ImportError:
            pass

if __name__ == '__main__':
    unittest.main()
