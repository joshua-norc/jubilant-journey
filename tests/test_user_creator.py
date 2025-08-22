import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from src.user_creator import create_salesforce_users

class TestUserCreator(unittest.TestCase):

    def setUp(self):
        """Set up sample data for tests."""
        self.mock_sf = MagicMock()
        self.sample_data = pd.DataFrame({
            'Username': ['test1@example.com'],
            'Alias': ['test1'],
            'FirstName': ['Test'],
            'LastName': ['One'],
            'Email (name version)': ['test1@example.com'],
            'ProfileID': ['prof1'],
            'RoleID': ['role1'],
            'TimeZoneSidKey': ['America/New_York'],
            'LocaleSidKey': ['en_US'],
            'LanguageLocaleKey': ['en_US'],
            'EmailEncodingKey': ['UTF-8'],
            'IsActive': [True],
            'UserPermissionsInteractionUser': [False],
            'EnableSSO': [True],
            'FederationIdentifier': ['fed1'],
            'PermissionSetGroupIDs': ['psg1;psg2'],
            'Queues': ['Queue1\nQueue2']
        })
        # Configure the return values for the mocked Salesforce calls
        self.mock_sf.User.create.return_value = {'success': True, 'id': 'new_user_id_1'}
        self.mock_sf.query_all.return_value = {
            'records': [{'Name': 'Queue1', 'Id': 'q1_id'}, {'Name': 'Queue2', 'Id': 'q2_id'}]
        }

    def test_create_user_success(self):
        """Test the successful creation of a user with assignments."""
        created_ids = create_salesforce_users(self.mock_sf, self.sample_data, dry_run=False)

        # Check that a user was created
        self.mock_sf.User.create.assert_called_once()
        user_payload = self.mock_sf.User.create.call_args[0][0]
        self.assertEqual(user_payload['Username'], 'test1@example.com')
        self.assertEqual(user_payload['FederationIdentifier'], 'fed1')

        # Check that permission sets were assigned
        self.assertEqual(self.mock_sf.PermissionSetAssignment.create.call_count, 2)

        # Check that the queue query was made
        self.mock_sf.query_all.assert_called_once()

        # Check that users were added to queues
        self.assertEqual(self.mock_sf.GroupMember.create.call_count, 2)

        # Check that the created ID is returned
        self.assertEqual(created_ids, ['new_user_id_1'])

    def test_no_queues_to_query(self):
        """Test that the queue query is not run if there are no queues."""
        self.sample_data['Queues'] = None
        self.mock_sf.reset_mock() # Reset mocks for a clean test

        create_salesforce_users(self.mock_sf, self.sample_data, dry_run=False)

        # Assert that the queue query was NOT made
        self.mock_sf.query_all.assert_not_called()

    def test_dry_run(self):
        """Test that no API calls are made in dry-run mode."""
        self.mock_sf.reset_mock()

        created_ids = create_salesforce_users(self.mock_sf, self.sample_data, dry_run=True)

        self.mock_sf.User.create.assert_not_called()
        self.mock_sf.PermissionSetAssignment.create.assert_not_called()
        self.mock_sf.query_all.assert_not_called()
        self.mock_sf.GroupMember.create.assert_not_called()

        # Check that dummy IDs are returned
        self.assertEqual(created_ids, ['DRY_RUN_USER_ID_0'])

if __name__ == '__main__':
    unittest.main()
