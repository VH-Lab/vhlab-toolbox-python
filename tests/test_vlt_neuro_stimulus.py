
import unittest
import numpy as np
from vlt.neuro.stimulus.stimids2reps import stimids2reps
from vlt.neuro.stimulus.findcontrolstimulus import findcontrolstimulus

class TestStimIds2Reps(unittest.TestCase):
    def test_basic(self):
        stimids = [1, 2, 3, 1, 2, 3]
        numstims = 3
        reps, isregular = stimids2reps(stimids, numstims)
        np.testing.assert_array_equal(reps, [1, 1, 1, 2, 2, 2])
        self.assertTrue(isregular)

    def test_irregular(self):
        # [1, 2, 3, 3, 2, 1] is regular (each set has {1,2,3})
        stimids_reg = [1, 2, 3, 3, 2, 1]
        numstims = 3
        reps, isregular = stimids2reps(stimids_reg, numstims)
        self.assertTrue(isregular)

        # Truly irregular: duplicates in one block, missing in another
        stimids_irreg = [1, 2, 3, 1, 1, 2]
        reps, isregular = stimids2reps(stimids_irreg, numstims)
        self.assertFalse(isregular)

    def test_incomplete(self):
        stimids = [1, 2, 3, 1, 2]
        numstims = 3
        reps, isregular = stimids2reps(stimids, numstims)
        np.testing.assert_array_equal(reps, [1, 1, 1, 2, 2])
        self.assertTrue(isregular)

class TestFindControlStimulus(unittest.TestCase):
    def test_regular(self):
        stimid = [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3]
        controlstimid = 3
        cs = findcontrolstimulus(stimid, [controlstimid])
        # Indices in MATLAB: 3, 6, 9, 12, 15
        # Expected indices in result (0-based): 2, 2, 2, 5, 5, 5...
        expected = []
        expected.extend([2]*3)
        expected.extend([5]*3)
        expected.extend([8]*3)
        expected.extend([11]*3)
        expected.extend([14]*3)
        np.testing.assert_array_equal(cs, expected)

if __name__ == '__main__':
    unittest.main()
