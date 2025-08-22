import unittest
from unittest.mock import MagicMock
import pandas as pd
from src.preflight import run_duplicate_check

class TestPreflight(unittest.TestCase):

    def setUp(self):
        """Set up a mock Salesforce connection and sample data."""
        self.mock_sf = MagicMock()
        self.users_to_add = pd.DataFrame({
            'Email (name version)': ['new@example.com', 'existing@example.com'],
            'Username': ['new_user', 'existing_user'],
            'FirstName': ['New', 'Existing'],
            'LastName': ['User', 'User']
        })

    def test_duplicate_check(self):
        """Test that duplicates are correctly identified."""
        # Mock the query results to simulate one existing user
        self.mock_sf.query_all.side_effect = [
            # Email query result
            {'records': [{'Id': '005_existing_email', 'Email': 'existing@example.com', 'Name': 'Existing User'}]},
            # Username query result
            {'records': [{'Id': '005_existing_user', 'Username': 'existing_user', 'Name': 'Existing User'}]}
        ]

        report_df = run_duplicate_check(self.mock_sf, self.users_to_add)

        self.assertEqual(len(report_df), 2)
        # Check the new user
        new_user_row = report_df[report_df['Username'] == 'new_user']
        self.assertEqual(new_user_row['Action'].iloc[0], 'Create New User')

        # Check the existing user
        existing_user_row = report_df[report_df['Username'] == 'existing_user']
        self.assertEqual(existing_user_row['Action'].iloc[0], 'Skip - Duplicate Found')
        self.assertIn('Email match', existing_user_row['Notes'].iloc[0])

    def test_no_duplicates_found(self):
        """Test that no duplicates are found when none exist."""
        self.mock_sf.query_all.return_value = {'records': []}

        report_df = run_duplicate_check(self.mock_sf, self.users_to_add)

        self.assertEqual(len(report_df), 2)
        self.assertTrue((report_df['Action'] == 'Create New User').all())

if __name__ == '__main__':
    unittest.main()
