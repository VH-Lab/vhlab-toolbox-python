import unittest
import numpy as np
from vlt.graph.mergegraph import mergegraph

class TestGraph(unittest.TestCase):
    def test_mergegraph(self):
        G1 = np.array([[1, 1, 1], [0, 1, 0], [0, 0, 1]])
        G2 = np.array([[1, 1], [0, 1]])
        nodenumbers2_1 = [1, 4] # Node 1 matches Node 1 of G1. Node 4 is new (since G1 has 3 nodes).

        # In MATLAB example:
        # G1 3x3. n1=3.
        # nodenumbers2_1 = [1, 4].
        # 4 > 3, so new node. 1 <= 3, old node.
        # newnodes = [4]. oldnodes = [1].
        # numnewnodes = 1.

        merged_graph, indexes, numnewnodes = mergegraph(G1, G2, nodenumbers2_1)

        self.assertEqual(numnewnodes, 1)
        self.assertEqual(merged_graph.shape, (4, 4))

        # Check values
        # newnode is index 4 (1-based), so index 3 (0-based) in merged graph.
        # oldnode is index 1 (1-based), so index 0 (0-based) in merged graph.

        # lower_right: G2(new, new). G2 new index is 2nd node (index 1 0-based).
        # G2[1,1] is 1.
        # merged_graph[3,3] should be 1.
        self.assertEqual(merged_graph[3, 3], 1)

        # lower_left: row=new, col=old. merged_graph[3, 0].
        # G2(new, old). G2[1, 0] is 0.
        self.assertEqual(merged_graph[3, 0], 0)

        # upper_right: row=old, col=new. merged_graph[0, 3].
        # G2(old, new). G2[0, 1] is 1.
        self.assertEqual(merged_graph[0, 3], 1)

        # Check defaults
        # merged_graph[3, 1] (new, old2) should be inf
        self.assertTrue(np.isinf(merged_graph[3, 1]))

        # Check G1 part preserved
        np.testing.assert_array_equal(merged_graph[0:3, 0:3], G1)

    def test_mergegraph_errors(self):
        G1 = np.eye(2)
        G2 = np.eye(2)
        # No new nodes
        with self.assertRaisesRegex(ValueError, 'At least one of the nodes of G2'):
            mergegraph(G1, G2, [1, 2])

        # Non-square
        with self.assertRaisesRegex(ValueError, 'G1 not square'):
            mergegraph(np.ones((2,3)), G2, [1, 3])

if __name__ == '__main__':
    unittest.main()
