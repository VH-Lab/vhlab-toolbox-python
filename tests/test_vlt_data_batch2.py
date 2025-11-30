import unittest
import vlt.data
import numpy as np

class TestDataFunctionsBatch2(unittest.TestCase):

    def test_string2cell(self):
        s = 'a,b, c '
        # Default trimws=True
        self.assertEqual(vlt.data.string2cell(s, ','), ['a', 'b', 'c'])
        # trimws=False
        self.assertEqual(vlt.data.string2cell(s, ',', trimws=False), ['a', 'b', ' c '])

        # Multiple separators
        s2 = 'a,,b'
        self.assertEqual(vlt.data.string2cell(s2, ','), ['a', '', 'b'])

    def test_structfullfields(self):
        s = {'a': 1, 'b': {'c': 2, 'd': {'e': 3}}}
        fields = vlt.data.structfullfields(s)
        # Order might vary depending on dict iteration order, but Python 3.7+ preserves insertion order.
        # Recursion order: a, b, b.c, b.d, b.d.e
        expected = ['a', 'b', 'b.c', 'b.d', 'b.d.e']
        self.assertEqual(set(fields), set(expected))

        with self.assertRaises(TypeError):
            vlt.data.structfullfields("not a dict")

    def test_structmerge(self):
        s1 = {'a': 1, 'b': 2}
        s2 = {'b': 3, 'c': 4}

        merged = vlt.data.structmerge(s1, s2)
        self.assertEqual(merged, {'a': 1, 'b': 3, 'c': 4})

        # Order check (alphabetical default)
        self.assertEqual(list(merged.keys()), ['a', 'b', 'c'])

        # Error if new field
        with self.assertRaises(ValueError):
            vlt.data.structmerge(s1, s2, error_if_new_field=True)

        # No error if new field is False
        vlt.data.structmerge(s1, s2, error_if_new_field=False)

        # Alphabetical false
        merged_unordered = vlt.data.structmerge(s1, s2, do_alphabetical=False)
        # Python 3.7+ dicts preserve insertion order. s1 keys, then s2 new keys.
        # a, b, c
        self.assertEqual(list(merged_unordered.keys()), ['a', 'b', 'c'])

    def test_structwhatvaries(self):
        s1 = {'a': 1, 'b': 2}
        s2 = {'a': 1, 'b': 3}
        s3 = {'a': 1, 'b': 2, 'c': 4}

        # s1 vs s2: b varies
        self.assertEqual(vlt.data.structwhatvaries([s1, s2]), ['b'])

        # s1 vs s3: c varies (present in one not other)
        self.assertEqual(vlt.data.structwhatvaries([s1, s3]), ['c'])

        # s1, s2, s3: b and c vary
        self.assertEqual(vlt.data.structwhatvaries([s1, s2, s3]), ['b', 'c'])

        # Identical
        self.assertEqual(vlt.data.structwhatvaries([s1, s1]), [])

        # Empty
        self.assertEqual(vlt.data.structwhatvaries([]), [])

        # Type check
        with self.assertRaises(TypeError):
            vlt.data.structwhatvaries("not a list")

    def test_tabstr2struct(self):
        s = '1\t2.5\tstring\t2023-01-01'
        fields = ['a', 'b', 'c', 'd']
        res = vlt.data.tabstr2struct(s, fields)

        self.assertEqual(res['a'], 1.0)
        self.assertEqual(res['b'], 2.5)
        self.assertEqual(res['c'], 'string')
        self.assertEqual(res['d'], '2023-01-01')

        # Date with slashes
        s2 = '01/01/2023'
        res2 = vlt.data.tabstr2struct(s2, ['date'])
        self.assertEqual(res2['date'], '01/01/2023')

        # Numeric failure
        s3 = 'notanumber'
        res3 = vlt.data.tabstr2struct(s3, ['val'])
        self.assertEqual(res3['val'], 'notanumber')

    def test_var2struct(self):
        a = 1
        b = 2

        res = vlt.data.var2struct('a', 'b')
        self.assertEqual(res, {'a': 1, 'b': 2})

        with self.assertRaises(KeyError):
            vlt.data.var2struct('nonexistent')

    def test_workspace2struct(self):
        x = 10
        y = 20
        _z = 30 # hidden

        res = vlt.data.workspace2struct()

        self.assertIn('x', res)
        self.assertEqual(res['x'], 10)
        self.assertIn('y', res)
        self.assertEqual(res['y'], 20)

        # Should not contain _z
        self.assertNotIn('_z', res)

        # Should contain 'self' (the test case instance)
        self.assertIn('self', res)

if __name__ == '__main__':
    unittest.main()
