import unittest
from vlt.db.struct_name_value_search import struct_name_value_search

class TestStructNameValueSearch(unittest.TestCase):
    def test_basic_search(self):
        thestruct = [
            {'name': 'param1', 'value': 10},
            {'name': 'param2', 'value': 20},
            {'name': 'param3', 'value': 30}
        ]

        val = struct_name_value_search(thestruct, 'param2')
        self.assertEqual(val, 20)

        val = struct_name_value_search(thestruct, 'param1')
        self.assertEqual(val, 10)

    def test_not_found_error(self):
        thestruct = [
            {'name': 'param1', 'value': 10}
        ]
        with self.assertRaises(ValueError):
            struct_name_value_search(thestruct, 'param2')

    def test_not_found_no_error(self):
        thestruct = [
            {'name': 'param1', 'value': 10}
        ]
        val = struct_name_value_search(thestruct, 'param2', makeerror=False)
        self.assertIsNone(val)

    def test_missing_fields(self):
        thestruct = [{'value': 10}] # Missing name
        with self.assertRaisesRegex(ValueError, "must have a field named 'name'"):
             struct_name_value_search(thestruct, 'param1')

        thestruct = [{'name': 'param1'}] # Missing value
        with self.assertRaisesRegex(ValueError, "must have a field named 'value'"):
             struct_name_value_search(thestruct, 'param1')

    def test_empty_struct(self):
        thestruct = []
        with self.assertRaises(ValueError):
            struct_name_value_search(thestruct, 'param1')

        val = struct_name_value_search(thestruct, 'param1', makeerror=False)
        self.assertIsNone(val)

    def test_multiple_matches(self):
        # Should return the first match
        thestruct = [
            {'name': 'param1', 'value': 10},
            {'name': 'param1', 'value': 999}
        ]
        val = struct_name_value_search(thestruct, 'param1')
        self.assertEqual(val, 10)

if __name__ == '__main__':
    unittest.main()
