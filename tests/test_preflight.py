import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import os
import tempfile
from main import handle_preflight # Import the handler from main

class TestPreflightCommand(unittest.TestCase):

    def setUp(self):
        """Set up mock objects and a temporary directory."""
        self.mock_sf = MagicMock()
        self.test_dir = tempfile.TemporaryDirectory()
        # This test relies on the excel file created by `create_test_excel.py`
        self.input_excel_path = 'reports/test_users.xlsx'
        self.output_csv_path = os.path.join(self.test_dir.name, 'preflight.csv')
        self.mock_config = MagicMock()
        self.connect_patcher = patch('main.connect_to_salesforce', return_value=self.mock_sf)
        self.connect_patcher.start()

    def tearDown(self):
        """Clean up and stop patches."""
        self.test_dir.cleanup()
        self.connect_patcher.stop()

    def test_preflight_command_with_duplicates(self):
        """Test the preflight command when duplicates are found."""
        # Mock the SF query to return one of the users from the test file
        self.mock_sf.query_all.return_value = {
            'records': [{'Id': '005_existing_user', 'Email': 'Brunt-Kelli@norc.org', 'Username': 'Brunt-Kelli@norc.org@test.com', 'Name': 'Kelli Brunt'}]
        }

        mock_args = MagicMock()
        mock_args.input = self.input_excel_path
        mock_args.output = self.output_csv_path

        handle_preflight(mock_args, self.mock_config)

        self.assertTrue(os.path.exists(self.output_csv_path))
        report_df = pd.read_csv(self.output_csv_path)

        # There are 3 users in the test file, 1 is a duplicate
        self.assertEqual(len(report_df), 3)
        skipped_rows = report_df[report_df['Action'] == 'Skip - Duplicate Found']
        self.assertEqual(len(skipped_rows), 1)
        self.assertEqual(skipped_rows.iloc[0]['FirstName'], 'Kelli')

    def test_preflight_command_no_duplicates(self):
        """Test the preflight command when no duplicates are found."""
        self.mock_sf.query_all.return_value = {'records': []}

        mock_args = MagicMock()
        mock_args.input = self.input_excel_path
        mock_args.output = self.output_csv_path

        handle_preflight(mock_args, self.mock_config)

        report_df = pd.read_csv(self.output_csv_path)
        self.assertTrue((report_df['Action'] == 'Create New User').all())

if __name__ == '__main__':
    unittest.main()
