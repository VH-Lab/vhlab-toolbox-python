import unittest
import os
import numpy as np
import vlt.file.custom_file_formats as cff

class TestCustomFileFormats(unittest.TestCase):
    def setUp(self):
        self.spike_file = 'test_spike.vhl'
        self.vhsb_file = 'test.vhsb'
        self.lock_file = 'test.vhsb-lock'

    def tearDown(self):
        for f in [self.spike_file, self.vhsb_file, self.lock_file]:
            if os.path.exists(f):
                os.remove(f)

    def test_spike_waveform(self):
        params = {
            'numchannels': 2,
            'S0': -5,
            'S1': 5,
            'name': 'Test Spike',
            'ref': 1,
            'comment': 'A comment',
            'samplingrate': 1000.0
        }

        cff.newvhlspikewaveformfile(self.spike_file, params)

        # Add waveforms
        # Format: [samples, channels, waveforms]
        # samples per channel = 5 - (-5) + 1 = 11
        # channels = 2
        # waveforms = 3

        waveforms = np.zeros((11, 2, 3))
        waveforms[:, :, 0] = 1 # Waveform 1 is all 1s
        waveforms[:, :, 1] = 2 # Waveform 2 is all 2s
        waveforms[:, :, 2] = 3 # Waveform 3 is all 3s

        cff.addvhlspikewaveformfile(self.spike_file, waveforms)

        # Read back
        w, p = cff.readvhlspikewaveformfile(self.spike_file)

        self.assertEqual(p['numchannels'], 2)
        self.assertEqual(p['S0'], -5)
        self.assertEqual(p['S1'], 5)
        self.assertEqual(p['name'], 'Test Spike')
        self.assertEqual(p['samplingrate'], 1000.0)

        self.assertEqual(w.shape, (11, 2, 3))
        self.assertTrue(np.allclose(w[:,:,0], 1))
        self.assertTrue(np.allclose(w[:,:,1], 2))
        self.assertTrue(np.allclose(w[:,:,2], 3))

    def test_vhsb_read_write(self):
        # Create dummy data
        # X: 100 samples
        x = np.arange(100) * 0.1
        # Y: 100 samples x 2 channels
        y = np.random.rand(100, 2)

        # Write
        cff.vhsb_write(self.vhsb_file, x, y, X_units='s', Y_units='V')

        # Read Header
        h = cff.vhsb_readheader(self.vhsb_file)
        self.assertEqual(h['X_units'], 's')
        self.assertEqual(h['Y_units'], 'V')
        self.assertEqual(h['num_samples'], 100)

        # Read Data
        y_read, x_read = cff.vhsb_read(self.vhsb_file, 0, 10) # Time 0 to 10 (all)

        # Note: floating point precision might differ slightly due to float32/64 conversions
        # Default X is float64? No, MATLAB default is float32 (4 bytes) unless specified?
        # vhsb_write default X_data_type is 'float' (4), size 64?
        # MATLAB vhsb_write defaults: X_data_size=64, X_data_type='float' (4).
        # vhsb_sampletype2matlabfwritestring(4, 64) -> 'float64' (double)
        # So it uses double precision.

        self.assertTrue(np.allclose(x, x_read))
        self.assertTrue(np.allclose(y, y_read))
