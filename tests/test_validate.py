import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import os
import tempfile
from main import handle_validate # Import the handler from main

class TestValidateCommand(unittest.TestCase):

    def setUp(self):
        """Set up mock objects and temporary files."""
        self.mock_sf = MagicMock()
        self.test_dir = tempfile.TemporaryDirectory()

        self.results_csv_path = os.path.join(self.test_dir.name, 'results.csv')
        self.source_excel_path = 'dummy_source.xlsx' # This file doesn't need to exist for the test

        # Create a dummy results CSV with the necessary Username column
        results_data = {
            'Username': ['user_josh', 'user_not_josh', 'user_failed'],
            'Status': ['Success', 'Success', 'Failed'],
            'SalesforceId': ['005_josh', '005_not_josh', None]
        }
        pd.DataFrame(results_data).to_csv(self.results_csv_path, index=False)

        # Create a dummy source dataframe that will be returned by the mocked read_excel
        self.source_data = pd.DataFrame({
            'Username': ['user_josh', 'user_not_josh', 'user_failed'],
            'added by': ['Josh', 'Not Josh', 'Josh']
        })

        self.mock_config = MagicMock()
        self.connect_patcher = patch('main.connect_to_salesforce', return_value=self.mock_sf)
        self.connect_patcher.start()

        self.validate_patcher = patch('main.validate_created_users')
        self.mock_validate_users = self.validate_patcher.start()

        # Patch pandas.read_excel to return our dummy source data
        self.read_excel_patcher = patch('pandas.read_excel', return_value=self.source_data)
        self.read_excel_patcher.start()

    def tearDown(self):
        """Clean up and stop patches."""
        self.test_dir.cleanup()
        self.connect_patcher.stop()
        self.validate_patcher.stop()
        self.read_excel_patcher.stop()

    def test_validate_command(self):
        """Test that the validation is correctly filtered by the 'added by' column."""
        mock_args = MagicMock()
        mock_args.input = self.results_csv_path
        mock_args.excel_source = self.source_excel_path

        handle_validate(mock_args, self.mock_config)

        self.mock_validate_users.assert_called_once()

        # Check that it was called with only the ID from the user added by 'Josh'
        called_with_ids = self.mock_validate_users.call_args[0][1]
        self.assertEqual(called_with_ids, ['005_josh'])

if __name__ == '__main__':
    unittest.main()
