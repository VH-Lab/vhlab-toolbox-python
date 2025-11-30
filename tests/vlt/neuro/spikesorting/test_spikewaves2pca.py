import unittest
import numpy as np
from vlt.neuro.spikesorting.spikewaves2pca import spikewaves2pca

class TestSpikeWaves2PCA(unittest.TestCase):
    def test_spikewaves2pca(self):
        # Create synthetic data
        # 3 spikes, 10 samples, 1 channel
        # Spike 1: sine wave
        # Spike 2: -sine wave
        # Spike 3: cosine wave

        S = 10
        C = 1
        K = 100

        t = np.linspace(0, 2*np.pi, S)
        wave1 = np.sin(t)
        wave2 = -np.sin(t)

        waves = np.zeros((S, C, K))
        for i in range(K):
            if i % 2 == 0:
                waves[:, 0, i] = wave1
            else:
                waves[:, 0, i] = wave2

        # With just two shapes (sine and -sine), 1 PC should explain 100% variance.

        N = 2
        features = spikewaves2pca(waves, N)

        self.assertEqual(features.shape, (N, K))

        # Check that PC1 separates the two groups
        pc1 = features[0, :]
        # Even indices should have similar PC1, odd indices similar PC1, and they should be opposite.

        mean_even = np.mean(pc1[0::2])
        mean_odd = np.mean(pc1[1::2])

        # They should be far apart (signs might vary depending on SVD sign ambiguity)
        self.assertTrue(abs(mean_even - mean_odd) > 0.1)
        # Standard deviations should be small (identical waves)
        self.assertTrue(np.std(pc1[0::2]) < 1e-5)
        self.assertTrue(np.std(pc1[1::2]) < 1e-5)

    def test_multichannel(self):
        # S=5, C=2, K=10
        waves = np.random.randn(5, 2, 10)
        N = 3
        features = spikewaves2pca(waves, N)
        self.assertEqual(features.shape, (N, 10))

    def test_range(self):
        waves = np.random.randn(10, 1, 5)
        # Range 1 to 5
        rng = [1, 5]
        N = 2
        # Should use only first 5 samples
        features = spikewaves2pca(waves, N, rng=rng)

        # Manually compute to verify
        sub_waves = waves[0:5, :, :]
        features_manual = spikewaves2pca(sub_waves, N)

        np.testing.assert_allclose(features, features_manual)

if __name__ == '__main__':
    unittest.main()
