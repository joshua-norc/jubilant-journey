import unittest
import pandas as pd
import os
import tempfile
from src.mapper import load_mapping, map_row_to_payload

class TestMapper(unittest.TestCase):

    def setUp(self):
        """Set up a temporary mapping file."""
        self.test_dir = tempfile.TemporaryDirectory()
        self.mapping_path = os.path.join(self.test_dir.name, "mapping.properties")
        with open(self.mapping_path, 'w') as f:
            f.write("# This is a comment\n")
            f.write("FirstName=FirstName\n")
            f.write("LastName=LastName\n")
            f.write("Email\ (employee\ ID\ version)=Email\n")

    def tearDown(self):
        """Clean up the temporary directory."""
        self.test_dir.cleanup()

    def test_load_mapping(self):
        """Test that the mapping file is loaded correctly."""
        mapping = load_mapping(self.mapping_path)
        self.assertIsNotNone(mapping)
        self.assertEqual(len(mapping), 3)
        self.assertEqual(mapping['FirstName'], 'FirstName')
        self.assertEqual(mapping['Email (employee ID version)'], 'Email')

    def test_map_row_to_payload(self):
        """Test that a data row is correctly mapped to a payload."""
        mapping = load_mapping(self.mapping_path)
        row = pd.Series({
            'FirstName': 'Test',
            'LastName': 'User',
            'Email (employee ID version)': 'test@example.com',
            'Extra Column': 'Should be ignored'
        })

        payload = map_row_to_payload(row, mapping)

        self.assertEqual(len(payload), 3)
        self.assertEqual(payload['FirstName'], 'Test')
        self.assertEqual(payload['LastName'], 'User')
        self.assertEqual(payload['Email'], 'test@example.com')
        self.assertNotIn('Extra Column', payload)

if __name__ == '__main__':
    unittest.main()
