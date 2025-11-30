import unittest
import numpy as np
import pandas as pd
import vlt.data

class TestVltDataNew(unittest.TestCase):

    def test_dropnan(self):
        a = [1, 2, np.nan, 3]
        b = vlt.data.dropnan(a)
        self.assertTrue(np.array_equal(b, [1, 2, 3]))

        c = [np.nan, np.nan]
        d = vlt.data.dropnan(c)
        self.assertEqual(len(d), 0)

    def test_emptystruct(self):
        s = vlt.data.emptystruct('a', 'b')
        self.assertEqual(s, [])

    def test_emptytable(self):
        t = vlt.data.emptytable('a', 'double', 'b', 'string')
        self.assertIsInstance(t, pd.DataFrame)
        self.assertTrue('a' in t.columns)
        self.assertTrue('b' in t.columns)
        self.assertEqual(len(t), 0)

        with self.assertRaises(ValueError):
            vlt.data.emptytable('a')

    def test_eqlen(self):
        self.assertTrue(vlt.data.eqlen([1, 2], [1, 2]))
        self.assertFalse(vlt.data.eqlen([1, 2], [1, 2, 3]))
        self.assertFalse(vlt.data.eqlen([1, 2], [1, 3]))
        self.assertTrue(vlt.data.eqlen(1, 1))

    def test_equnique(self):
        a = [1, 2, 3, 2, 1]
        u = vlt.data.equnique(a)
        self.assertEqual(sorted(u), [1, 2, 3])

        # Test with objects that might fail with hash-based unique
        # Lists are not hashable
        l = [[1, 2], [3, 4], [1, 2]]
        u_l = vlt.data.equnique(l)
        self.assertEqual(len(u_l), 2)
        # We can't easily sort list of lists, so check membership
        self.assertTrue([1, 2] in u_l)
        self.assertTrue([3, 4] in u_l)

    def test_fieldsearch(self):
        A = {'a': 'test', 'b': 1, 'c': {'d': 2}}

        # Exact string
        s1 = {'field': 'a', 'operation': 'exact_string', 'param1': 'test'}
        self.assertTrue(vlt.data.fieldsearch(A, s1))

        s2 = {'field': 'a', 'operation': 'exact_string', 'param1': 'other'}
        self.assertFalse(vlt.data.fieldsearch(A, s2))

        # Greater than
        s3 = {'field': 'b', 'operation': 'greaterthan', 'param1': 0}
        self.assertTrue(vlt.data.fieldsearch(A, s3))

        # Has field
        s4 = {'field': 'c', 'operation': 'hasfield'}
        self.assertTrue(vlt.data.fieldsearch(A, s4))

        # OR
        s5 = {'operation': 'or',
              'param1': {'field': 'a', 'operation': 'exact_string', 'param1': 'wrong'},
              'param2': {'field': 'b', 'operation': 'exact_number', 'param1': 1}}
        self.assertTrue(vlt.data.fieldsearch(A, s5))

    def test_findclosest(self):
        arr = [1, 5, 10]
        idx, val = vlt.data.findclosest(arr, 6)
        self.assertEqual(idx, 1) # index of 5
        self.assertEqual(val, 5)

        idx, val = vlt.data.findclosest([], 6)
        self.assertIsNone(idx)

    def test_findrowvec(self):
        a = [[1, 2], [3, 4], [1, 2]]
        b = [1, 2]
        idx = vlt.data.findrowvec(a, b)
        self.assertTrue(np.array_equal(idx, [0, 2]))

        idx = vlt.data.findrowvec(a, [5, 6])
        self.assertEqual(len(idx), 0)

    def test_flattenstruct2table(self):
        # S.A.X = [10, 20], S.A.Y = ['a', 'b'], S.C = 3
        # In python: [{'A': {'X': 10, 'Y': 'a'}, 'C': 3}, {'A': {'X': 20, 'Y': 'b'}, 'C': 3}]
        # Wait, the example in MATLAB was:
        # Sub = struct('X', {10, 20}, 'Y', {'a', 'b'}); % A 1x2 struct array
        # S = struct('A', Sub, 'C', 3);
        # This implies S is 1x1, containing A which is 1x2.

        # Python input equivalent:
        s = [{
            'A': [{'X': 10, 'Y': 'a'}, {'X': 20, 'Y': 'b'}],
            'C': 3
        }]

        t = vlt.data.flattenstruct2table(s)

        self.assertEqual(len(t), 1)
        self.assertTrue('A.X' in t.columns)
        self.assertTrue('A.Y' in t.columns)
        self.assertTrue('C' in t.columns)

        # Check values
        # A.X should be [10, 20]
        self.assertEqual(t.iloc[0]['A.X'], [10, 20])
        self.assertEqual(t.iloc[0]['C'], 3)

        # Check renaming
        t2 = vlt.data.flattenstruct2table(s, [['A.X', 'AX']])
        self.assertTrue('AX' in t2.columns)

if __name__ == '__main__':
    unittest.main()
