import unittest
from vlt.docs.markdownoutput2objectstruct import markdownoutput2objectstruct

class TestMarkdownOutput2ObjectStruct(unittest.TestCase):
    def test_simple_structure(self):
        markdown_output = [
            {'title': 'Object 1', 'path': '/path/to/obj1', 'url_prefix': 'prefix1'},
            {'title': 'Object 2', 'path': '/path/to/obj2', 'url_prefix': 'prefix2'}
        ]

        expected = [
            {'object': 'Object 1', 'path': '/path/to/obj1', 'url_prefix': 'prefix1'},
            {'object': 'Object 2', 'path': '/path/to/obj2', 'url_prefix': 'prefix2'}
        ]

        result = markdownoutput2objectstruct(markdown_output)
        self.assertEqual(result, expected)

    def test_nested_structure(self):
        # Nested structure
        # Item 2 has a path that is another list of items
        markdown_output = [
            {'title': 'Object 1', 'path': '/path/to/obj1', 'url_prefix': 'prefix1'},
            {'title': 'Group 1', 'path': [
                {'title': 'Object 2', 'path': '/path/to/obj2', 'url_prefix': 'prefix2'},
                {'title': 'Object 3', 'path': '/path/to/obj3', 'url_prefix': 'prefix3'}
            ], 'url_prefix': 'group_prefix'} # url_prefix of group might be ignored in recursion logic of MATLAB code
        ]

        expected = [
            {'object': 'Object 1', 'path': '/path/to/obj1', 'url_prefix': 'prefix1'},
            {'object': 'Object 2', 'path': '/path/to/obj2', 'url_prefix': 'prefix2'},
            {'object': 'Object 3', 'path': '/path/to/obj3', 'url_prefix': 'prefix3'}
        ]

        result = markdownoutput2objectstruct(markdown_output)
        self.assertEqual(result, expected)

    def test_empty_input(self):
        result = markdownoutput2objectstruct([])
        self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()
