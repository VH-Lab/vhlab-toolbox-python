"""VHSB must behave the way vhlab-toolbox-matlab's VHSB behaves.

The file format is a cross-language contract: NDI-matlab and NDI-python both
store an element's epoch data as ``epoch_binary_data.vhsb`` and each expects
to read what the other wrote. These tests pin the two places this port had
drifted from ``+vlt/+file/+custom_file_formats/vhsb_write.m`` and
``vhsb_read.m``.
"""

import os
import tempfile
import unittest
import warnings

import numpy as np

import vlt.file.custom_file_formats as cff
from vlt.signal import point2samplelabel


def _round_trip(path, x, y, x0=-np.inf, x1=np.inf):
    x = np.asarray(x, dtype=float).reshape(-1, 1)
    y = np.asarray(y, dtype=float)
    if y.ndim == 1:
        y = y.reshape(-1, 1)
    cff.vhsb_write(path, x, y, use_filelock=0)
    header = cff.vhsb_readheader(path)
    read_y, read_x = cff.vhsb_read(path, x0, x1)
    return header, np.asarray(read_x).ravel(), np.asarray(read_y), x, y


class TestTwoSampleSeries(unittest.TestCase):
    """MATLAB writes a 2-sample series; this port used to raise on it.

    vhsb_write.m guards the constant-interval test with ``numel(x)>3``, so it
    never evaluates ``max()`` on an empty array. This port used one
    ``len(x) > 1`` guard for both the increment and the interval test, so with
    two samples ``diff(diff(x))`` was empty and numpy raised
    "zero-size array to reduction operation maximum".
    """

    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def test_two_samples_can_be_written_and_read(self):
        path = os.path.join(self.dir, "two.vhsb")
        header, rx, ry, x, y = _round_trip(path, [0.25, 0.75], [1, 2])
        self.assertEqual(header["num_samples"], 2)
        self.assertTrue(np.array_equal(rx, x.ravel()))
        self.assertTrue(np.array_equal(ry.reshape(y.shape), y))

    def test_every_small_sample_count_round_trips(self):
        """1 through 5 samples: none of these may raise."""
        for n in (1, 2, 3, 4, 5):
            with self.subTest(n=n):
                path = os.path.join(self.dir, f"n{n}.vhsb")
                _, rx, ry, x, y = _round_trip(
                    path, np.arange(n) * 0.25, np.arange(n, dtype=float)
                )
                self.assertTrue(np.array_equal(rx, x.ravel()))
                self.assertTrue(np.array_equal(ry.reshape(y.shape), y))


class TestHeaderGuardsMatchMatlab(unittest.TestCase):
    """The sample-count thresholds are MATLAB's, exactly.

        if numel(x)>2, X_increment = median(diff(x)); else, X_increment = 0; end;
        if numel(x)>3, X_constantinterval = ...;      else, X_constantinterval = 0; end;

    A different threshold writes a different header for the same input, which
    is a cross-language difference in the file itself rather than in one
    reader.
    """

    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def _header_for(self, n):
        path = os.path.join(self.dir, f"h{n}.vhsb")
        x = (np.arange(n) * 0.25).reshape(-1, 1)
        y = np.arange(n, dtype=float).reshape(-1, 1)
        cff.vhsb_write(path, x, y, use_filelock=0)
        return cff.vhsb_readheader(path)

    def test_constant_interval_needs_more_than_three_samples(self):
        for n, expected in ((1, 0), (2, 0), (3, 0), (4, 1), (5, 1)):
            with self.subTest(n=n):
                self.assertEqual(self._header_for(n)["X_constantinterval"], expected)

    def test_increment_needs_more_than_two_samples(self):
        for n, expected in ((1, 0.0), (2, 0.0), (3, 0.25), (4, 0.25)):
            with self.subTest(n=n):
                self.assertEqual(self._header_for(n)["X_increment"], expected)


class TestMonotonicIntervalChange(unittest.TestCase):
    """A shrinking interval is not a constant interval.

    ``X_constantinterval`` is a magnitude test on the second difference of X,
    so it must be taken on ``abs()``. A series whose interval shrinks has an
    all-negative second difference, and ``max()`` of that is negative, which
    compares less than the tolerance. MATLAB wrote ``max(diff(diff(x)))`` with
    no ``abs()`` and so recorded such a series as constant-interval; the two
    languages disagreed for this input until
    VH-Lab/vhlab-toolbox-matlab#145 was fixed.

    X is stored in the file either way, so the flag does not change what a full
    read returns -- it changes which samples a WINDOWED read selects, because
    the constant-interval branch derives sample labels from ``X_increment``.
    """

    def setUp(self):
        self.dir = tempfile.mkdtemp()

    # intervals 1, 0.5, 0.25; median(diff(x)) is 0.5, which describes none of them
    SHRINKING = [0.0, 1.0, 1.5, 1.75]

    def test_shrinking_interval_is_not_constant(self):
        path = os.path.join(self.dir, "shrink.vhsb")
        header, rx, ry, x, y = _round_trip(path, self.SHRINKING, [1, 2, 3, 4])
        self.assertEqual(header["X_constantinterval"], 0)
        self.assertTrue(np.array_equal(rx, x.ravel()))

    def test_growing_interval_is_not_constant(self):
        path = os.path.join(self.dir, "grow.vhsb")
        header, _, _, _, _ = _round_trip(path, [0.0, 0.25, 0.75, 1.75], [1, 2, 3, 4])
        self.assertEqual(header["X_constantinterval"], 0)

    def test_windowed_read_of_a_shrinking_series(self):
        """The consequence of the flag: 1.5..1.75 is two samples, not one.

        Flagged constant-interval, point2samplelabel(1.5, 0.5, 0) is sample 4
        and 1.75 clips to 4 as well, so only the last sample comes back.
        """
        path = os.path.join(self.dir, "window.vhsb")
        x = np.asarray(self.SHRINKING).reshape(-1, 1)
        y = np.asarray([1.0, 2.0, 3.0, 4.0]).reshape(-1, 1)
        cff.vhsb_write(path, x, y, use_filelock=0)
        ry, rx = cff.vhsb_read(path, 1.5, 1.75)
        self.assertTrue(np.allclose(np.asarray(rx).ravel(), [1.5, 1.75]))
        self.assertTrue(np.allclose(np.asarray(ry).ravel(), [3.0, 4.0]))


class TestInfiniteBounds(unittest.TestCase):
    """Reading a whole constant-interval series with +/-Inf bounds.

    MATLAB's vhsb_read clips the sample labels into [1, num_samples], and
    clip(-Inf, [1 N]) is 1 while clip(Inf, [1 N]) is N, so +/-Inf selects the
    whole series. This port cast the labels to int BEFORE clipping, and numpy
    turns +/-Inf into an undefined integer, so the clip bounded garbage and
    exactly ONE sample came back.

    ndi.element.ensemble/spikeMatrix reads its epoch with
    readtimeseries(epoch, -Inf, Inf), so this is on a live path.
    """

    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def test_infinite_bounds_return_the_whole_series(self):
        path = os.path.join(self.dir, "reg.vhsb")
        header, rx, ry, x, y = _round_trip(
            path, np.arange(100) / 1000.0, np.arange(100, dtype=float)
        )
        self.assertEqual(header["X_constantinterval"], 1, "fixture must be constant-interval")
        self.assertEqual(len(rx), 100, "all 100 samples, not 1")
        self.assertTrue(np.array_equal(rx, x.ravel()))
        self.assertTrue(np.array_equal(ry.reshape(y.shape), y))

    def test_infinite_bounds_raise_no_numpy_warning(self):
        """The int cast warned "invalid value encountered in cast" first."""
        path = os.path.join(self.dir, "warn.vhsb")
        with warnings.catch_warnings():
            warnings.simplefilter("error", RuntimeWarning)
            _round_trip(path, np.arange(10) / 1000.0, np.arange(10, dtype=float))

    def test_finite_bounds_still_select_a_window(self):
        """The fix must not turn every read into a full read."""
        path = os.path.join(self.dir, "win.vhsb")
        x = (np.arange(100) / 1000.0).reshape(-1, 1)
        y = np.arange(100, dtype=float).reshape(-1, 1)
        cff.vhsb_write(path, x, y, use_filelock=0)
        _, rx = cff.vhsb_read(path, 0.010, 0.019)
        rx = np.asarray(rx).ravel()
        self.assertEqual(len(rx), 10)
        self.assertAlmostEqual(rx[0], 0.010)
        self.assertAlmostEqual(rx[-1], 0.019)


class TestPoint2SampleLabel(unittest.TestCase):
    """MATLAB's is double arithmetic with no integer cast."""

    def test_infinities_survive(self):
        s = point2samplelabel([-np.inf, np.inf], 0.001, 0.0)
        self.assertTrue(np.isneginf(s[0]))
        self.assertTrue(np.isposinf(s[1]))

    def test_finite_labels_are_unchanged(self):
        """1 + round((0.02 - 0) / 0.001) == 21, as before."""
        self.assertEqual(point2samplelabel(0.02, 0.001), 21)
        self.assertTrue(
            np.array_equal(point2samplelabel([0.0, 0.001, 0.002], 0.001), [1, 2, 3])
        )


class TestMarkedPointProcess(unittest.TestCase):
    """The case NDI needs: irregular timestamps that ARE the data.

    An ensemble epoch stores every spike of every neuron with the neuron
    column index as its mark. The timestamps are not on a grid, so they must
    survive the round trip exactly rather than being reconstructed from a
    sampling rate.
    """

    def test_irregular_timestamps_round_trip_exactly(self):
        path = os.path.join(tempfile.mkdtemp(), "mpp.vhsb")
        times = [0.125, 0.25, 0.375, 0.5, 0.75, 1.0, 1.5]
        marks = [1, 2, 1, 3, 2, 1, 3]
        header, rx, ry, x, y = _round_trip(path, times, marks)
        self.assertEqual(header["X_constantinterval"], 0, "irregular by construction")
        self.assertTrue(np.array_equal(rx, x.ravel()))
        self.assertTrue(np.array_equal(ry.reshape(y.shape), y))

    def test_multi_column_data_round_trips(self):
        path = os.path.join(tempfile.mkdtemp(), "mc.vhsb")
        _, rx, ry, x, y = _round_trip(
            path, [0.125, 0.5, 0.75, 1.5], [[1, 2], [3, 4], [5, 6], [7, 8]]
        )
        self.assertTrue(np.array_equal(rx, x.ravel()))
        self.assertTrue(np.array_equal(ry.reshape(y.shape), y))


if __name__ == "__main__":
    unittest.main()
