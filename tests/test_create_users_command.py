import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import os
import tempfile
from main import handle_create_users # Import the handler from main

class TestCreateUsersCommand(unittest.TestCase):

    def setUp(self):
        """Set up mock objects and temporary files."""
        self.mock_sf = MagicMock()
        self.test_dir = tempfile.TemporaryDirectory()

        self.preflight_csv_path = os.path.join(self.test_dir.name, 'preflight.csv')
        self.source_excel_path = 'reports/test_users.xlsx'
        self.output_csv_path = os.path.join(self.test_dir.name, 'results.csv')
        self.mapping_path = 'mapping.properties'

        preflight_data = {
            'Email (employee ID version)': ['002@norc.org'], 'Email (name version)': ['Cooper-Tina@norc.org'],
            'FirstName': ['Tina'], 'LastName': ['Cooper'], 'Persona Name': ['Tier 1 Rep - English'],
            'Username': ['Cooper-Tina@norc.org@test.com'], 'Action': ['Create New User'], 'Notes': ['']
        }
        pd.DataFrame(preflight_data).to_csv(self.preflight_csv_path, index=False)

        self.mock_config = MagicMock()
        self.mock_config.__getitem__.return_value = {'environment': 'Training', 'mapping_file': self.mapping_path}

        self.connect_patcher = patch('main.connect_to_salesforce', return_value=self.mock_sf)
        self.connect_patcher.start()

        # Mock the SF API calls that will be made
        self.mock_sf.User.create.return_value = {'success': True, 'id': '005_new_user'}
        # This mock is needed to prevent assignment errors for queues
        self.mock_sf.query_all.return_value = {'records': [{'Name': 'Queue2', 'Id': 'q2_id'}, {'Name': 'Queue3', 'Id': 'q3_id'}]}

    def tearDown(self):
        """Clean up."""
        self.test_dir.cleanup()
        self.connect_patcher.stop()

    def test_create_users_command_flow(self):
        """Test the create-users command handler from main.py."""
        mock_args = MagicMock()
        mock_args.input = self.preflight_csv_path
        mock_args.excel_source = self.source_excel_path
        mock_args.output = self.output_csv_path
        mock_args.dry_run = False

        handle_create_users(mock_args, self.mock_config)

        self.mock_sf.User.create.assert_called_once()

        payload = self.mock_sf.User.create.call_args[0][0]
        self.assertEqual(payload['Email'], '002@norc.org')
        self.assertEqual(payload['ProfileId'], 'prof2')

        self.assertTrue(os.path.exists(self.output_csv_path))
        results_df = pd.read_csv(self.output_csv_path)
        # With the queue query mocked, this should now be 'Success'
        self.assertEqual(results_df.iloc[0]['Status'], 'Success')
        self.assertEqual(results_df.iloc[0]['SalesforceId'], '005_new_user')

if __name__ == '__main__':
    unittest.main()
