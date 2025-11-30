import unittest
from vlt.docs.mkdocsnavtext import mkdocsnavtext

class TestMkDocsNavText(unittest.TestCase):
    def test_simple_structure(self):
        out = [
            {'title': 'Page 1', 'path': 'page1.md'},
            {'title': 'Page 2', 'path': 'page2.md'}
        ]
        expected = "  - Page 1: 'page1.md'\n  - Page 2: 'page2.md'\n"
        self.assertEqual(mkdocsnavtext(out, 2), expected)

    def test_nested_structure(self):
        out = [
            {'title': 'Section 1', 'path': [
                {'title': 'Page 1.1', 'path': 'page1.1.md'}
            ]},
            {'title': 'Page 2', 'path': 'page2.md'}
        ]
        expected = "  - Section 1:\n    - Page 1.1: 'page1.1.md'\n  - Page 2: 'page2.md'\n"
        self.assertEqual(mkdocsnavtext(out, 2), expected)

if __name__ == '__main__':
    unittest.main()
