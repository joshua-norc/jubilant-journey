import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from src.user_creator import create_salesforce_users

class TestUserCreator(unittest.TestCase):

    def setUp(self):
        """Set up sample data for tests."""
        self.mock_sf = MagicMock()
        self.sample_data = pd.DataFrame({
            'Username': ['test1@example.com'], 'Alias': ['test1'], 'FirstName': ['Test'], 'LastName': ['One'],
            'Email (name version)': ['test1@example.com'], 'ProfileID': ['prof1'], 'RoleID': ['role1'],
            'TimeZoneSidKey': ['America/New_York'], 'LocaleSidKey': ['en_US'], 'LanguageLocaleKey': ['en_US'],
            'EmailEncodingKey': ['UTF-8'], 'IsActive': [True], 'UserPermissionsInteractionUser': [False],
            'EnableSSO': [True], 'FederationIdentifier': ['fed1'], 'PermissionSetGroupIDs': ['psg1'], 'Queues': ['Queue1']
        })
        self.mock_sf.User.create.return_value = {'success': True, 'id': 'new_user_id_1'}
        self.mock_sf.query_all.return_value = {'records': [{'Name': 'Queue1', 'Id': 'q1_id'}]}

    def test_create_user_success_return_df(self):
        """Test the successful creation of a user and the returned DataFrame."""
        results_df = create_salesforce_users(self.mock_sf, self.sample_data, dry_run=False)

        self.assertIsInstance(results_df, pd.DataFrame)
        self.assertEqual(len(results_df), 1)

        result = results_df.iloc[0]
        self.assertEqual(result['Status'], 'Success')
        self.assertEqual(result['SalesforceId'], 'new_user_id_1')
        self.assertEqual(result['AssignmentErrors'], '')

    def test_user_creation_failure(self):
        """Test the handling of a user creation failure."""
        self.mock_sf.User.create.return_value = {'success': False, 'errors': ['Test Error']}

        results_df = create_salesforce_users(self.mock_sf, self.sample_data, dry_run=False)

        self.assertEqual(results_df.iloc[0]['Status'], 'Failed')
        self.assertIn('Test Error', results_df.iloc[0]['Error'])

    def test_assignment_failure(self):
        """Test the handling of a permission set assignment failure."""
        self.mock_sf.PermissionSetAssignment.create.side_effect = Exception("Assignment Failed")

        results_df = create_salesforce_users(self.mock_sf, self.sample_data, dry_run=False)

        result = results_df.iloc[0]
        self.assertEqual(result['Status'], 'Success with errors')
        self.assertIn('Assignment Failed', result['AssignmentErrors'])

    def test_dry_run_return_df(self):
        """Test the dry run returns the correct DataFrame."""
        results_df = create_salesforce_users(self.mock_sf, self.sample_data, dry_run=True)

        self.assertEqual(results_df.iloc[0]['Status'], 'Dry Run - Not Created')

if __name__ == '__main__':
    unittest.main()
