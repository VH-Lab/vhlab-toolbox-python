import unittest
import os
import vlt.file

class TestFile(unittest.TestCase):
    def setUp(self):
        self.filename = 'test_cellstr2text.txt'

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_cellstr2text(self):
        cs = ['a', 'b', 'c']
        vlt.file.cellstr2text(self.filename, cs)

        with open(self.filename, 'r') as f:
            content = f.read()
        self.assertEqual(content, 'a\nb\nc\n')

    def test_filename_value(self):
        self.assertEqual(vlt.file.filename_value('test.txt'), 'test.txt')

        class FileObj:
            def __init__(self, name):
                self.fullpathfilename = name

        obj = FileObj('test.txt')
        self.assertEqual(vlt.file.filename_value(obj), 'test.txt')
