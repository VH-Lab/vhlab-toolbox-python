import unittest
import numpy as np
import vlt.signal.point2samplelabel
import vlt.signal.samplelabel2point

class TestSignal(unittest.TestCase):
    def test_point2samplelabel(self):
        dt = 0.001
        ti = 0.02
        s = vlt.signal.point2samplelabel(ti, dt)
        self.assertEqual(s, 21) # 1 + 20

    def test_samplelabel2point(self):
        dt = 0.001
        s = 21
        ti = vlt.signal.samplelabel2point(s, dt)
        self.assertAlmostEqual(ti, 0.02)
