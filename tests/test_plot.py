import unittest
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from vlt.plot.myerrorbar import myerrorbar
from vlt.plot.plot_multichan import plot_multichan
from vlt.plot.supersubplot import supersubplot

# Use Agg backend to avoid GUI window issues during testing
matplotlib.use('Agg')

class TestPlotFunctions(unittest.TestCase):

    def test_myerrorbar(self):
        x = np.linspace(0, 10, 11)
        y = np.sin(x)
        e = np.ones_like(x) * 0.1

        # Test 1: myerrorbar(x, y, e)
        plt.figure()
        h = myerrorbar(x, y, e)
        self.assertTrue(len(h) > 0)
        plt.close()

        # Test 2: myerrorbar(y, e)
        plt.figure()
        h = myerrorbar(y, e)
        self.assertTrue(len(h) > 0)
        plt.close()

        # Test 3: myerrorbar(x, y, l, u)
        plt.figure()
        h = myerrorbar(x, y, e, e)
        self.assertTrue(len(h) > 0)
        plt.close()

        # Test 4: with symbol
        plt.figure()
        h = myerrorbar(x, y, e, 'r-')
        self.assertTrue(len(h) > 0)
        # Check color
        line = h[0]
        self.assertEqual(line.get_color(), 'r')
        plt.close()

    def test_plot_multichan(self):
        data = np.random.rand(100, 3)
        t = np.arange(100)
        space = 5

        plt.figure()
        h = plot_multichan(data, t, space)
        self.assertEqual(len(h), 3)
        plt.close()

    def test_supersubplot(self):
        fig = plt.figure()
        m = 2
        n = 2

        # Plot 1: Should be on first figure
        ax1 = supersubplot(fig, m, n, 1)
        self.assertEqual(ax1.figure, fig)

        # Plot 5: Should be on second figure (since 2x2=4 per figure)
        ax5 = supersubplot(fig, m, n, 5)
        self.assertNotEqual(ax5.figure, fig)

        # Check if they are linked
        # The first figure should track the second one
        self.assertTrue(hasattr(fig, '_supersubplot_figures'))
        self.assertEqual(fig._supersubplot_figures[2], ax5.figure)

        plt.close('all')

if __name__ == '__main__':
    unittest.main()
