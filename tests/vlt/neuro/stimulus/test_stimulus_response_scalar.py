import sys
import types
import unittest

import numpy as np

import vlt.neuro.stimulus.stimulus_response_scalar  # noqa: F401  (populates sys.modules)
import vlt.neuro.vision.oridir.index.oridir_fitindexes  # noqa: F401
import vlt.neuro.vision.oridir.index.oridir_vectorindexes  # noqa: F401
from vlt.neuro.stimulus.stimulus_response_scalar import stimulus_response_scalar
from vlt.neuro.vision.oridir.index.oridir_vectorindexes import oridir_vectorindexes


class TestHelperImportsAreFunctions(unittest.TestCase):
    """`import vlt.pkg.mod as alias` binds the *function* when `pkg/__init__.py`
    re-exports that name, so `alias.mod(...)` raises AttributeError. These modules
    must import the callables directly."""

    HELPERS = {
        'vlt.neuro.stimulus.stimulus_response_scalar': [
            'findcontrolstimulus', 'fouriercoeffs_tf2', 'fouriercoeffs_tf_spikes',
        ],
        'vlt.neuro.vision.oridir.index.oridir_vectorindexes': [
            'hotellingt2test', 'compute_circularvariance', 'compute_orientationindex',
            'compute_tuningwidth', 'compute_dircircularvariance', 'compute_directionindex',
            'compute_directionsignificancedotproduct',
        ],
        'vlt.neuro.vision.oridir.index.oridir_fitindexes': [
            'otfit_carandini', 'fit2fitoi', 'fit2fitoidiffsum', 'fit2fitdi',
            'fit2fitdidiffsum',
        ],
    }

    def test_helpers_are_callables_not_modules(self):
        for module_name, helper_names in self.HELPERS.items():
            module = sys.modules[module_name]
            for helper_name in helper_names:
                with self.subTest(module=module_name, helper=helper_name):
                    helper = getattr(module, helper_name, None)
                    self.assertIsNotNone(helper, f'{module_name} does not import {helper_name}')
                    self.assertNotIsInstance(helper, types.ModuleType)
                    self.assertTrue(callable(helper))


class TestStimulusResponseScalarF0(unittest.TestCase):
    """Continuous (non-spike) mean responses."""

    def setUp(self):
        # six 2 s stimuli separated by 1 s gaps, each holding a constant value
        self.onsets = np.array([
            [0.0, 2.0, 1],
            [3.0, 5.0, 2],
            [6.0, 8.0, 3],
            [9.0, 11.0, 1],
            [12.0, 14.0, 2],
            [15.0, 17.0, 3],
        ])
        self.values = [5.0, 1.0, 7.0, 6.0, 2.0, 8.0]
        self.timestamps = np.arange(0.0, 18.0005, 0.001)
        self.timeseries = np.zeros_like(self.timestamps)
        for (onset, offset, _), value in zip(self.onsets, self.values):
            inside = (self.timestamps >= onset) & (self.timestamps <= offset)
            self.timeseries[inside] = value

    def test_mean_response_and_control(self):
        r = stimulus_response_scalar(self.timeseries, self.timestamps, self.onsets,
                                     freq_response=0, control_stimid=[2])
        np.testing.assert_array_equal(r['stimid'], [1, 2, 3, 1, 2, 3])
        np.testing.assert_allclose(r['response'], self.values)
        # stimulus 2 is the control; reps 1 and 2 use rows 1 and 4 respectively
        np.testing.assert_array_equal(r['controlstimnumber'], [1, 1, 1, 4, 4, 4])
        np.testing.assert_allclose(r['control_response'], [1.0, 1.0, 1.0, 2.0, 2.0, 2.0])

    def test_f0_response_stays_real(self):
        r = stimulus_response_scalar(self.timeseries, self.timestamps, self.onsets,
                                     freq_response=0, control_stimid=[2])
        # MATLAB grows `response = []`, so an F0 run yields a real array
        self.assertFalse(np.iscomplexobj(r['response']))
        self.assertFalse(np.iscomplexobj(r['control_response']))


class TestStimulusResponseScalarF1(unittest.TestCase):
    """A non-zero freq_response yields Fourier coefficients, which are complex."""

    def setUp(self):
        self.onsets = np.array([
            [0.0, 2.0, 1],
            [2.0, 4.0, 2],
            [4.0, 6.0, 1],
            [6.0, 8.0, 2],
        ])
        self.timestamps = np.arange(0.0, 8.0005, 0.001)
        self.timeseries = np.zeros_like(self.timestamps)
        first = (self.timestamps >= 0.0) & (self.timestamps <= 2.0)
        third = (self.timestamps >= 4.0) & (self.timestamps <= 6.0)
        self.timeseries[first] = np.sin(2 * np.pi * self.timestamps[first])
        self.timeseries[third] = 3 * np.sin(2 * np.pi * self.timestamps[third])

    def test_f1_is_complex_and_recovers_amplitude(self):
        r = stimulus_response_scalar(self.timeseries, self.timestamps, self.onsets,
                                     freq_response=1, control_stimid=[2])
        self.assertTrue(np.iscomplexobj(r['response']))
        self.assertTrue(np.iscomplexobj(r['control_response']))
        # fouriercoeffs_tf2 normalizes by 2/N, so |F1| is the sine's amplitude
        np.testing.assert_allclose(np.abs(r["response"][0]), 1.0, atol=5e-3)
        np.testing.assert_allclose(np.abs(r["response"][2]), 3.0, atol=5e-3)
        # the blank stimuli carry no signal
        np.testing.assert_allclose(np.abs(r['response'][[1, 3]]), [0.0, 0.0], atol=1e-9)


class TestStimulusResponseScalarSpikes(unittest.TestCase):
    """Spike rates: MATLAB divides the stimulus, control and prestimulus counts
    alike by the *stimulus's* duration."""

    def test_control_rate_uses_stimulus_duration(self):
        # 2 s stimuli alternating with 4 s controls, so the two durations differ
        onsets = np.array([
            [0.0, 2.0, 1],
            [2.0, 6.0, 2],
            [6.0, 8.0, 1],
            [8.0, 12.0, 2],
        ])
        spiketimes = np.array([
            0.1, 0.5, 1.0, 1.5,               # 4 spikes in stimulus row 0 (2 s)
            2.5, 3.0, 3.5, 4.0, 4.5, 5.0,     # 6 spikes in control row 1 (4 s)
            6.5, 7.5,                          # 2 spikes in stimulus row 2 (2 s)
            8.5, 9.5, 10.5,                    # 3 spikes in control row 3 (4 s)
        ])
        timeseries = np.ones_like(spiketimes)

        r = stimulus_response_scalar(timeseries, spiketimes, onsets,
                                     freq_response=0, control_stimid=[2], isspike=1)

        np.testing.assert_array_equal(r['controlstimnumber'], [1, 1, 3, 3])
        # row 0: 4 spikes / 2 s; row 1: 6 spikes / 4 s; row 2: 2 / 2; row 3: 3 / 4
        np.testing.assert_allclose(r['response'], [2.0, 1.5, 1.0, 0.75])
        # row 0's control holds 6 spikes but is divided by row 0's 2 s duration,
        # not by its own 4 s (dividing by 4 would give 1.5 and 0.75)
        np.testing.assert_allclose(r['control_response'], [3.0, 1.5, 1.5, 0.75])

    def test_prestimulus_rate_uses_stimulus_duration(self):
        onsets = np.array([
            [10.0, 14.0, 1],
            [20.0, 24.0, 2],
        ])
        spiketimes = np.array([
            9.2, 9.6,                                        # 2 spikes in [9, 10)
            10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 13.5, 13.9,  # 8 spikes in [10, 14]
            19.5,                                            # 1 spike in [19, 20)
            20.5, 21.5, 22.5, 23.5,                          # 4 spikes in [20, 24]
        ])
        timeseries = np.ones_like(spiketimes)

        r = stimulus_response_scalar(timeseries, spiketimes, onsets,
                                     freq_response=0, control_stimid=[2], isspike=1,
                                     prestimulus_time=1.0,
                                     prestimulus_normalization='subtract')

        # row 0: 8/4 s stimulus rate minus a 2/4 s prestimulus rate. Dividing the
        # prestimulus count by prestimulus_time (2/1) would give 0.0 instead.
        np.testing.assert_allclose(r['response'], [1.5, 0.75])
        # row 0's control is row 1: (4 spikes / 4 s) - (1 spike / 4 s)
        np.testing.assert_allclose(r['control_response'], [0.75, 0.75])


class TestOridirVectorIndexes(unittest.TestCase):
    """oridir_vectorindexes reaches hotellingt2test, which was shadowed by the
    same module-alias bug."""

    def test_runs_and_returns_finite_indexes(self):
        rng = np.random.default_rng(0)
        angles = np.arange(0.0, 360.0, 45.0)
        mean_resp = 1 + 10 * np.exp(-0.5 * (((angles - 90 + 180) % 360 - 180) / 30.0) ** 2)
        ind = np.array([mean_resp[i] + rng.normal(0, 0.5, 5) for i in range(len(angles))])
        curve = np.vstack([angles, mean_resp, ind.std(axis=1), ind.std(axis=1) / np.sqrt(5)])

        vi = oridir_vectorindexes({'curve': curve, 'ind': ind})

        for key in ('ot_HotellingT2_p', 'dir_HotellingT2_p', 'dir_dotproduct_sig_p'):
            self.assertTrue(np.isfinite(vi[key]), key)
            self.assertGreaterEqual(vi[key], 0.0)
            self.assertLessEqual(vi[key], 1.0)
        self.assertAlmostEqual(vi['dir_pref'], 90.0, delta=5.0)


if __name__ == '__main__':
    unittest.main()
