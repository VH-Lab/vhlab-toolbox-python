import unittest
import os
import shutil
import numpy as np
import vlt
import vlt.app.log
import vlt.data
import vlt.file
from vlt.toolboxdir import toolboxdir

class TestVlt(unittest.TestCase):
    def setUp(self):
        # Setup for logging tests
        if os.path.exists('test_logs'):
            shutil.rmtree('test_logs')
        os.makedirs('test_logs')

    def tearDown(self):
        if os.path.exists('test_logs'):
            shutil.rmtree('test_logs')

    def test_vlt_app_log(self):
        sys_log = os.path.join('test_logs', 'sys.log')
        err_log = os.path.join('test_logs', 'error.log')
        debug_log = os.path.join('test_logs', 'debug.log')

        log = vlt.app.log.Log(system_logfile=sys_log, error_logfile=err_log, debug_logfile=debug_log, system_verbosity=1)

        self.assertTrue(os.path.exists(sys_log))

        log.msg('system', 1, 'test message')

        with open(sys_log, 'r') as f:
            content = f.read()
            self.assertIn('test message', content)
            self.assertIn('SYSTEM', content)

    def test_vlt_data_assign(self):
        d = vlt.data.assign('a', 1, 'b', 2)
        self.assertEqual(d, {'a': 1, 'b': 2})

        d2 = vlt.data.assign({'a': 1, 'b': 2})
        self.assertEqual(d2, {'a': 1, 'b': 2})

    def test_vlt_data_cell2str(self):
        res = vlt.data.cell2str(['a', 1])
        self.assertEqual(res, "['a', 1]")
        self.assertEqual(vlt.data.cell2str([]), '[]')

    def test_vlt_data_cellarray2mat(self):
        c = [[1, 2, 3], [4, 5]]
        m = vlt.data.cellarray2mat(c)
        self.assertEqual(m.shape, (3, 2))
        self.assertEqual(m[0, 0], 1)
        self.assertEqual(m[1, 0], 2)
        self.assertEqual(m[2, 0], 3)
        self.assertEqual(m[0, 1], 4)
        self.assertEqual(m[1, 1], 5)
        self.assertTrue(np.isnan(m[2, 1]))

    def test_vlt_data_celloritem(self):
        l = [10, 20, 30]
        self.assertEqual(vlt.data.celloritem(l, 1), 20)
        self.assertEqual(vlt.data.celloritem(100), 100)

        # Check bounds
        with self.assertRaises(IndexError):
            vlt.data.celloritem(l, 5)

    def test_vlt_data_colvec(self):
        a = [[1, 2], [3, 4]]
        v = vlt.data.colvec(a)
        self.assertEqual(v.shape, (4, 1))
        # Default numpy flatten is row-major (C-style)
        # [1, 2, 3, 4]
        self.assertEqual(v[0, 0], 1)
        self.assertEqual(v[1, 0], 2)
        self.assertEqual(v[2, 0], 3)
        self.assertEqual(v[3, 0], 4)

    def test_vlt_data_conditional(self):
        self.assertEqual(vlt.data.conditional(1, 'a', 'b'), 'a')
        self.assertEqual(vlt.data.conditional(0, 'a', 'b'), 'b')
        self.assertEqual(vlt.data.conditional(-1, 'a', 'b'), 'b')

    def test_toolboxdir(self):
        path = toolboxdir()
        # Ensure it points to a valid directory
        self.assertTrue(os.path.isdir(path))
        # Ensure it contains 'vlt' subdirectory
        self.assertTrue(os.path.isdir(os.path.join(path, 'vlt')))
        # Verify it matches expected logic
        expected = os.path.dirname(os.path.dirname(os.path.abspath(vlt.__file__)))
        self.assertEqual(path, expected)

if __name__ == '__main__':
    unittest.main()
