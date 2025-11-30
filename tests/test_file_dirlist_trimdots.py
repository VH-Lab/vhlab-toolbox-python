import unittest
from vlt.file.dirlist_trimdots import dirlist_trimdots

class TestDirListTrimDots(unittest.TestCase):
    def test_string_list(self):
        dirlist = ['.', '..', 'file1', 'dir1', '.git', '__pycache__', '.DS_Store']
        expected = ['file1', 'dir1']
        self.assertEqual(dirlist_trimdots(dirlist), expected)

    def test_struct_list_output_struct(self):
        dirlist = [
            {'name': '.', 'isdir': True},
            {'name': '..', 'isdir': True},
            {'name': 'file1', 'isdir': False},
            {'name': 'dir1', 'isdir': True},
            {'name': '.git', 'isdir': True}
        ]
        expected = [
            {'name': 'file1', 'isdir': False},
            {'name': 'dir1', 'isdir': True}
        ]
        self.assertEqual(dirlist_trimdots(dirlist, output_struct=True), expected)

    def test_struct_list_no_output_struct(self):
        # Should return names of directories only
        dirlist = [
            {'name': '.', 'isdir': True},
            {'name': '..', 'isdir': True},
            {'name': 'file1', 'isdir': False},
            {'name': 'dir1', 'isdir': True},
            {'name': '.git', 'isdir': True}
        ]
        expected = ['dir1']
        self.assertEqual(dirlist_trimdots(dirlist, output_struct=False), expected)

    def test_empty_list(self):
        self.assertEqual(dirlist_trimdots([]), [])

if __name__ == '__main__':
    unittest.main()
