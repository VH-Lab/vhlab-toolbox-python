import unittest
import os
from vlt.matlab.isclassfile import isclassfile

class TestIsClassFile(unittest.TestCase):
    def setUp(self):
        self.class_file = 'temp_class.m'
        with open(self.class_file, 'w') as f:
            f.write("classdef MyClass\n   properties\n   end\nend\n")

        self.func_file = 'temp_func.m'
        with open(self.func_file, 'w') as f:
            f.write("function y = myfunc(x)\n y = x;\nend\n")

        self.script_file = 'temp_script.m'
        with open(self.script_file, 'w') as f:
            f.write("% comment\nx = 1;\n")

        self.class_with_comments = 'temp_class_comments.m'
        with open(self.class_with_comments, 'w') as f:
            f.write("% This is a class\nclassdef MyClassWithComments\nend\n")

    def tearDown(self):
        for f in [self.class_file, self.func_file, self.script_file, self.class_with_comments]:
            if os.path.exists(f):
                os.remove(f)

    def test_is_class_file(self):
        self.assertTrue(isclassfile(self.class_file))
        self.assertFalse(isclassfile(self.func_file))
        self.assertFalse(isclassfile(self.script_file))
        self.assertTrue(isclassfile(self.class_with_comments))

if __name__ == '__main__':
    unittest.main()
