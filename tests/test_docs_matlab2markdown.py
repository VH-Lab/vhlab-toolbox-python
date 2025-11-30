import unittest
import os
import shutil
from vlt.docs.matlab2markdown import matlab2markdown

class TestMatlab2Markdown(unittest.TestCase):
    def setUp(self):
        self.input_dir = 'temp_input_docs'
        self.output_dir = 'temp_output_docs'
        os.makedirs(self.input_dir, exist_ok=True)

        # Create a sample .m function
        with open(os.path.join(self.input_dir, 'myfunc.m'), 'w') as f:
            f.write("function myfunc()\n% This is a test function\n% Detailed help\n")

        # Create a sample package
        os.makedirs(os.path.join(self.input_dir, '+mypkg'), exist_ok=True)
        with open(os.path.join(self.input_dir, '+mypkg', 'pkgfunc.m'), 'w') as f:
            f.write("function pkgfunc()\n% Pkg function help\n")

        # Create a sample class
        with open(os.path.join(self.input_dir, 'MyClass.m'), 'w') as f:
            f.write("classdef MyClass\n% MyClass help\nproperties\nP1\nend\nmethods\nfunction foo()\n% foo help\nend\nend\nend\n")

    def tearDown(self):
        shutil.rmtree(self.input_dir)
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

    def test_matlab2markdown(self):
        out = matlab2markdown(self.input_dir, self.output_dir, 'docs')

        # Verify output structure
        self.assertTrue(len(out) > 0)

        # Check if files were created
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'myfunc.m.md')))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, '+mypkg', 'pkgfunc.m.md')))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'MyClass.m.md')))

        # Check content
        with open(os.path.join(self.output_dir, 'myfunc.m.md'), 'r') as f:
            content = f.read()
            self.assertIn("# myfunc", content)
            self.assertIn("This is a test function", content)

        with open(os.path.join(self.output_dir, 'MyClass.m.md'), 'r') as f:
            content = f.read()
            self.assertIn("# CLASS MyClass", content)
            self.assertIn("MyClass help", content)
            self.assertIn("foo help", content)

if __name__ == '__main__':
    unittest.main()
