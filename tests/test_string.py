import unittest
import numpy as np
from vlt.string.intseq2str import intseq2str
from vlt.string.line_n import line_n
from vlt.string.str2intseq import str2intseq
from vlt.string.strcmp_substitution import strcmp_substitution
from vlt.string.trimws import trimws

class TestIntSeq2Str(unittest.TestCase):
    def test_intseq2str_simple(self):
        A = [1, 2, 3, 7, 10]
        s = intseq2str(A)
        self.assertEqual(s, '1-3,7,10')

    def test_intseq2str_single(self):
        A = [5]
        s = intseq2str(A)
        self.assertEqual(s, '5')

    def test_intseq2str_empty(self):
        A = []
        s = intseq2str(A)
        self.assertEqual(s, '')

    def test_intseq2str_custom_sep(self):
        A = [1, 2, 5]
        s = intseq2str(A, sep=';')
        self.assertEqual(s, '1-2;5')

    def test_intseq2str_unsorted(self):
        # [3, 2, 1] -> diffs are -1. Not +1. So no compression.
        A = [3, 2, 1]
        s = intseq2str(A)
        self.assertEqual(s, '3,2,1')

    def test_intseq2str_numpy(self):
        # Test with numpy array to ensure truthiness check works
        A = np.array([1, 2, 3])
        s = intseq2str(A)
        self.assertEqual(s, '1-3')

        A = np.array([])
        s = intseq2str(A)
        self.assertEqual(s, '')

class TestLineN(unittest.TestCase):
    def test_line_n_simple(self):
        s = "Line 1\nLine 2\nLine 3"
        l, pos, eol_marks = line_n(s, 2)
        self.assertEqual(l, "Line 2")
        self.assertEqual(pos, 8)

    def test_line_n_first(self):
        s = "Line 1\nLine 2"
        l, pos, eol_marks = line_n(s, 1)
        self.assertEqual(l, "Line 1")
        self.assertEqual(pos, 1)

    def test_line_n_custom_eol(self):
        s = "Line 1|Line 2"
        l, pos, eol_marks = line_n(s, 2, eol='|')
        self.assertEqual(l, "Line 2")

    def test_line_n_out_of_bounds(self):
        s = "Line 1"
        with self.assertRaises(Exception):
            line_n(s, 2)

class TestStr2IntSeq(unittest.TestCase):
    def test_str2intseq_simple(self):
        s = '1-3,7,10,12'
        a = str2intseq(s)
        self.assertEqual(a, [1, 2, 3, 7, 10, 12])

    def test_str2intseq_single(self):
        s = '5'
        a = str2intseq(s)
        self.assertEqual(a, [5])

    def test_str2intseq_empty(self):
        s = ''
        a = str2intseq(s)
        self.assertEqual(a, [])

    def test_str2intseq_custom_sep(self):
        s = '1-2;5'
        a = str2intseq(s, sep=';')
        self.assertEqual(a, [1, 2, 5])

    def test_str2intseq_whitespace(self):
        s = ' 1 - 3 , 7 '
        a = str2intseq(s)
        self.assertEqual(a, [1, 2, 3, 7])

class TestStrcmpSubstitution(unittest.TestCase):
    def test_strcmp_subst_simple(self):
        s1 = 'test#.txt'
        s2 = ['test1.txt', 'test2.txt', 'other.txt']
        tf, match, subst = strcmp_substitution(s1, s2)

        self.assertEqual(tf, [True, True, False])
        self.assertEqual(match, ['test1.txt', 'test2.txt', ''])
        self.assertEqual(subst, ['1', '2', ''])

    def test_strcmp_subst_single(self):
        s1 = 'test#.txt'
        s2 = 'test123.txt'
        tf, match, subst = strcmp_substitution(s1, s2)

        self.assertTrue(tf)
        self.assertEqual(match, 'test123.txt')
        self.assertEqual(subst, '123')

    def test_strcmp_subst_fixed(self):
        s1 = 'test#.txt'
        s2 = ['testA.txt', 'testB.txt']
        # Force substitute string to be 'A'
        tf, match, subst = strcmp_substitution(s1, s2, SubstituteString='A')

        self.assertEqual(tf, [True, False])
        self.assertEqual(subst, ['A', ''])

    def test_strcmp_regex(self):
        s1 = '.*\.txt'
        s2 = ['my.txt', 'other.doc']
        tf, match, subst = strcmp_substitution(s1, s2, UseSubstituteString=False)
        self.assertEqual(tf, [True, False])

class TestTrimWs(unittest.TestCase):
    def test_trimws(self):
        s = '   hello '
        self.assertEqual(trimws(s), 'hello ')

    def test_trimws_empty(self):
        self.assertEqual(trimws(''), '')

    def test_trimws_none(self):
        self.assertEqual(trimws('hello'), 'hello')

if __name__ == '__main__':
    unittest.main()
