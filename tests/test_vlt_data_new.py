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

    def test_rowvec(self):
        # Test with 1D array
        a = [1, 2, 3]
        rv = vlt.data.rowvec(a)
        self.assertEqual(rv.shape, (1, 3))
        self.assertTrue(np.array_equal(rv, [[1, 2, 3]]))

        # Test with 2D array
        b = [[1], [2], [3]] # Column vector
        rv = vlt.data.rowvec(b)
        self.assertEqual(rv.shape, (1, 3))
        self.assertTrue(np.array_equal(rv, [[1, 2, 3]]))

    def test_nanstderr(self):
        # Test with no NaNs
        a = [1, 2, 3]
        se = vlt.data.nanstderr(a)
        # std(1,2,3) = 1. n = 3. se = 1/sqrt(3) = 0.57735...
        self.assertAlmostEqual(se, 1.0/np.sqrt(3))

        # Test with NaNs
        b = [1, 2, np.nan, 3]
        se = vlt.data.nanstderr(b)
        self.assertAlmostEqual(se, 1.0/np.sqrt(3))

        # Test with dim
        c = [[1, 2, 3], [4, 5, 6]]
        se = vlt.data.nanstderr(c, dim=1) # along rows
        self.assertEqual(len(se), 2)
        self.assertAlmostEqual(se[0], 1.0/np.sqrt(3))
        self.assertAlmostEqual(se[1], 1.0/np.sqrt(3))

    def test_matrow2cell(self):
        # Test 2D
        m = np.array([[1, 2], [3, 4]])
        c = vlt.data.matrow2cell(m)
        self.assertEqual(len(c), 2)
        self.assertTrue(np.array_equal(c[0], [[1, 2]]))
        self.assertTrue(np.array_equal(c[1], [[3, 4]]))

        # Test 1D
        v = np.array([1, 2, 3])
        c = vlt.data.matrow2cell(v)
        self.assertEqual(len(c), 1)
        self.assertTrue(np.array_equal(c[0], [[1, 2, 3]]))

    def test_prettyjson(self):
        d = {'a': 1, 'b': np.array([1, 2])}
        s = vlt.data.prettyjson(d)
        import json
        # Parse back and check
        d2 = json.loads(s)
        self.assertEqual(d2['a'], 1)
        self.assertEqual(d2['b'], [1, 2])
        # Check indentation roughly
        self.assertTrue('\n' in s)
        self.assertTrue('    ' in s)

    def test_partial_struct_match(self):
        A = {'a': 1, 'b': 2, 'c': {'d': 3, 'e': 4}}

        # Exact match subset
        B1 = {'a': 1}
        self.assertTrue(vlt.data.partial_struct_match(A, B1))

        # Recursive match
        B2 = {'c': {'d': 3}}
        self.assertTrue(vlt.data.partial_struct_match(A, B2))

        # Mismatch value
        B3 = {'a': 2}
        self.assertFalse(vlt.data.partial_struct_match(A, B3))

        # Missing key in A
        B4 = {'z': 1}
        self.assertFalse(vlt.data.partial_struct_match(A, B4))

        # Recursive mismatch
        B5 = {'c': {'d': 5}}
        self.assertFalse(vlt.data.partial_struct_match(A, B5))
        
    def test_hasAllFields(self):
        r = {'test1': 5, 'test2': [6, 1]} # In python [6, 1] is length 2.

        # In Python list [6, 1] is 1x2 in our logic? or 2x1?
        # Our logic for list says sz = (1, len). So (1, 2).

        # Case 1: All present, sizes match
        # Matlab example: r = struct('test1',5,'test2',[6 1]);
        # hasAllFields(r, {'test1','test2'}, {[1 1],[1 2]}) -> good=1

        # Here 'test1' is scalar 5 -> 1x1.
        # 'test2' is [6, 1] -> 1x2 (as list).

        good, err = vlt.data.hasAllFields(r, ['test1', 'test2'], [[1, 1], [1, 2]])
        self.assertTrue(good, err)

        # Case 2: Missing field
        good, err = vlt.data.hasAllFields(r, ['test1', 'test3'])
        self.assertFalse(good)
        self.assertIn("'test3' not present", err)

        # Case 3: Wrong size
        # Check size [1, 3] for test2 (which is 1x2)
        good, err = vlt.data.hasAllFields(r, ['test2'], [[1, 3]])
        self.assertFalse(good)
        self.assertIn("not of expected size", err)

        # Case 4: Ignore dimension
        good, err = vlt.data.hasAllFields(r, ['test2'], [[1, -1]])
        self.assertTrue(good, err)

    def test_hashmatlabvariable(self):
        d = {'a': 1, 'b': 2}
        h1 = vlt.data.hashmatlabvariable(d)
        h2 = vlt.data.hashmatlabvariable(d)
        self.assertEqual(h1, h2)
        self.assertIsInstance(h1, str)

        h3 = vlt.data.hashmatlabvariable(d, algorithm='pm_hash/crc')
        self.assertIsInstance(h3, int)

        d2 = {'a': 1, 'b': 3}
        h4 = vlt.data.hashmatlabvariable(d2)
        self.assertNotEqual(h1, h4)

    def test_isint(self):
        self.assertTrue(vlt.data.isint(5))
        self.assertTrue(vlt.data.isint(5.0))
        self.assertTrue(vlt.data.isint(np.array([1, 2, 3])))
        self.assertTrue(vlt.data.isint(np.array([1.0, 2.0, 3.0])))

        self.assertFalse(vlt.data.isint(5.5))
        self.assertFalse(vlt.data.isint(np.array([1.0, 2.5])))
        self.assertFalse(vlt.data.isint(np.nan))
        self.assertFalse(vlt.data.isint(np.inf))

    def test_islikevarname(self):
        good, err = vlt.data.islikevarname('validName')
        self.assertTrue(good)
        self.assertEqual(err, '')

        good, err = vlt.data.islikevarname('1invalid')
        self.assertFalse(good)
        self.assertIn('must begin with a letter', err)

        good, err = vlt.data.islikevarname('invalid name')
        self.assertFalse(good)
        self.assertIn('must have no whitespace', err)

        good, err = vlt.data.islikevarname('')
        self.assertFalse(good)
        self.assertIn('must be at least one character', err)

        good, err = vlt.data.islikevarname(123)
        self.assertFalse(good)
        self.assertIn('must be a character string', err)

    def test_jsonencodenan(self):
        obj = {'a': np.nan, 'b': np.inf, 'c': -np.inf, 'd': 5}
        json_str = vlt.data.jsonencodenan(obj)

        # Python json puts NaN, Infinity, -Infinity directly into output if allow_nan=True (default)
        # But this is not standard JSON.
        # Matlab's jsonencode with ConvertInfAndNaN=false does this too?
        # The description says "allows the use of NaN and -Inf and Inf".

        self.assertIn('NaN', json_str)
        self.assertIn('Infinity', json_str)

        # Test numpy array handling
        obj2 = {'arr': np.array([1, 2, 3])}
        json_str2 = vlt.data.jsonencodenan(obj2)
        self.assertIn('[', json_str2)
        self.assertIn('1', json_str2)

if __name__ == '__main__':
    unittest.main()
