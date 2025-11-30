import unittest
from vlt.neuro.spikesorting.cluster_initializeclusterinfo import cluster_initializeclusterinfo

class TestClusterInitializeClusterInfo(unittest.TestCase):
    def test_cluster_initializeclusterinfo(self):
        info = cluster_initializeclusterinfo()
        self.assertIsInstance(info, list)
        self.assertEqual(len(info), 0)

if __name__ == '__main__':
    unittest.main()
