import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import os
import tempfile
from src.reporter import generate_report

class TestReporter(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory for reports."""
        self.test_dir = tempfile.TemporaryDirectory()
        # This time, we will patch 'os.path.join' to redirect any file
        # being written to the 'reports' folder to our temp directory.
        self.original_join = os.path.join
        def custom_join(*args):
            if args and args[0] == 'reports':
                return self.original_join(self.test_dir.name, *args[1:])
            return self.original_join(*args)

        self.join_patch = patch('src.reporter.os.path.join', side_effect=custom_join)
        self.join_patch.start()

    def tearDown(self):
        """Clean up the temporary directory and stop patches."""
        self.test_dir.cleanup()
        self.join_patch.stop()

    @patch('src.reporter.os.makedirs')
    @patch('src.reporter.os.path.exists', return_value=True)
    def test_generate_report(self, mock_path_exists, mock_makedirs):
        """Test the successful generation of a report."""
        mock_sf = MagicMock()
        mock_query_result = {
            'totalSize': 1, 'done': True,
            'records': [
                {'attributes': {}, 'Id': '005xx0000012345', 'Username': 'testuser@example.com', 'Name': 'Test User', 'Email': 'testuser@example.com', 'Profile': {'Name': 'Standard User'}, 'UserRole': {'Name': 'CEO'}, 'FederationIdentifier': 'testuser', 'IsActive': True}
            ]
        }
        mock_sf.query_all.return_value = mock_query_result

        user_ids = ['005xx0000012345']

        generate_report(mock_sf, user_ids)

        # Check that a report was created in the temp dir
        self.assertEqual(len(os.listdir(self.test_dir.name)), 1, "A report file should have been created in the temp directory.")
        report_filename = os.listdir(self.test_dir.name)[0]
        self.assertTrue(report_filename.startswith('user_creation_report_'))

        # Check the content of the report
        report_df = pd.read_csv(os.path.join(self.test_dir.name, report_filename))
        self.assertEqual(len(report_df), 1)
        self.assertEqual(report_df.iloc[0]['Id'], '005xx0000012345')
        self.assertEqual(report_df.iloc[0]['ProfileName'], 'Standard User')
        self.assertEqual(report_df.iloc[0]['UserRoleName'], 'CEO')

    def test_no_users_to_report(self):
        """Test that no report is generated if the user_ids list is empty."""
        mock_sf = MagicMock()
        generate_report(mock_sf, [])
        self.assertEqual(len(os.listdir(self.test_dir.name)), 0, "No report file should be created for an empty user list.")

if __name__ == '__main__':
    unittest.main()
