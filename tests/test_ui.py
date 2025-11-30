import unittest
from vlt.ui.basicuitools_defs import basicuitools_defs

class TestBasicUIToolsDefs(unittest.TestCase):
    def test_basicuitools_defs_defaults(self):
        defs = basicuitools_defs()

        self.assertIn('button', defs)
        self.assertEqual(defs['button']['Style'], 'pushbutton')
        self.assertEqual(defs['button']['Units'], 'pixels')
        self.assertEqual(defs['button']['BackgroundColor'], [0.94, 0.94, 0.94])

    def test_basicuitools_defs_custom(self):
        defs = basicuitools_defs(uiUnits='normalized', uiBackgroundColor=[1, 0, 0])

        self.assertEqual(defs['button']['Units'], 'normalized')
        self.assertEqual(defs['button']['BackgroundColor'], [1, 0, 0])
        self.assertEqual(defs['txt']['Units'], 'normalized')

if __name__ == '__main__':
    unittest.main()
