import unittest
import os
from vlt.file.str2text import str2text

class TestStr2Text(unittest.TestCase):
    def setUp(self):
        self.filename = 'temp_str2text.txt'

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_write_text(self):
        content = "Hello, world!\nLine 2"
        str2text(self.filename, content)

        with open(self.filename, 'r', encoding='utf-8') as f:
            read_content = f.read()

        self.assertEqual(read_content, content)

    def test_write_error(self):
        # Use a directory as filename to trigger error (on Linux)
        if os.name == 'posix':
            with self.assertRaises(IOError):
                str2text('.', 'fail')

if __name__ == '__main__':
    unittest.main()
