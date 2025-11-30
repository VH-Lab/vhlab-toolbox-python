import unittest
import os
from vlt.docs.class2help import class2help

class TestClass2Help(unittest.TestCase):
    def setUp(self):
        self.filename = 'TempClass.m'
        content = """
classdef TempClass < SuperClass
    % TempClass - A temporary class for testing.
    %
    % This class is used to test class2help.

    properties
        Prop1 % Documentation for Prop1
        Prop2 = 10 % Documentation for Prop2
    end

    methods
        function obj = TempClass()
            % Constructor
        end

        function out = myMethod(obj, arg)
            % myMethod - A test method
            %
            % Detailed help for myMethod.
            out = arg;
        end
    end
end
"""
        with open(self.filename, 'w') as f:
            f.write(content)

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_class2help(self):
        classhelp, prop_struct, methods_struct, superclassnames = class2help(self.filename)

        # Verify class help
        self.assertIn("TempClass - A temporary class for testing.", classhelp)
        self.assertIn("This class is used to test class2help.", classhelp)

        # Verify properties
        self.assertEqual(len(prop_struct), 2)
        self.assertEqual(prop_struct[0]['property'], 'Prop1')
        self.assertEqual(prop_struct[0]['doc'], 'Documentation for Prop1')
        self.assertEqual(prop_struct[1]['property'], 'Prop2')
        self.assertEqual(prop_struct[1]['doc'], 'Documentation for Prop2')

        # Verify methods
        self.assertEqual(len(methods_struct), 2)
        # Constructor
        self.assertEqual(methods_struct[0]['method'], 'TempClass')
        self.assertEqual(methods_struct[0]['description'], 'Constructor')

        # myMethod
        self.assertEqual(methods_struct[1]['method'], 'myMethod')
        self.assertEqual(methods_struct[1]['description'], 'myMethod - A test method')
        self.assertIn("Detailed help for myMethod", methods_struct[1]['help'])

        # Verify superclasses
        self.assertEqual(superclassnames, ['SuperClass'])

if __name__ == '__main__':
    unittest.main()
