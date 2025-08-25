import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import os
import tempfile
from main import handle_provision_workflow

class TestProvisionWorkflow(unittest.TestCase):

    def setUp(self):
        """Set up mocks and temporary files."""
        self.mock_sf = MagicMock()
        self.test_dir = tempfile.TemporaryDirectory()

        self.source_excel_path = 'reports/test_users.xlsx'
        self.output_csv_path = os.path.join(self.test_dir.name, 'final_report.csv')
        self.mapping_path = 'mapping.properties'

        self.mock_config = MagicMock()
        self.mock_config.__getitem__.return_value = {
            'environment': 'Training',
            'mapping_file': self.mapping_path
        }

        self.connect_patcher = patch('main.connect_to_salesforce', return_value=self.mock_sf)
        self.connect_patcher.start()

        self.preflight_patcher = patch('main.run_duplicate_check')
        self.mock_preflight = self.preflight_patcher.start()

        self.create_patcher = patch('main.create_salesforce_users')
        self.mock_create_users = self.create_patcher.start()

        self.validate_patcher = patch('main.validate_created_users')
        self.mock_validate_users = self.validate_patcher.start()

    def tearDown(self):
        """Clean up."""
        self.test_dir.cleanup()
        self.connect_patcher.stop()
        self.preflight_patcher.stop()
        self.create_patcher.stop()
        self.validate_patcher.stop()

    def test_provision_workflow_end_to_end(self):
        """Test that the main workflow handler calls all steps in sequence."""
        # This mock needs to be realistic and include the columns that will be processed later.
        preflight_return = pd.DataFrame({
            'Username': ['Brunt-Kelli@norc.org@test.com', 'Cooper-Tina@norc.org@test.com'],
            'Action': ['Skip - Duplicate Found', 'Create New User'],
            'Notes': ['Email match', ''],
            'Persona Name': ['Tier 1 Supervisor', 'Tier 1 Rep - English'],
            # Add other columns that are needed for processing...
            'Email (employee ID version)': ['001@norc.org', '002@norc.org'],
            'Email (name version)': ['Brunt-Kelli@norc.org', 'Cooper-Tina@norc.org'],
            'FirstName': ['Kelli', 'Tina'], 'LastName': ['Brunt', 'Cooper'],
            'Alias': ['kbrunt', 'tcooper'], 'TimeZoneSidKey': ['America/Chicago', 'America/New_York'],
            'LocaleSidKey': ['en_US', 'en_US'], 'LanguageLocaleKey': ['en_US', 'en_US'],
            'EmailEncodingKey': ['UTF-8', 'UTF-8'], 'IsActive': [True, True],
            'UserPermissionsInteractionUser': [True, False], 'Is_Migrated__c': [False, False],
            'Contact Center': ['center1', 'center2'], 'FederationIdentifier': ['kbrunt', 'tcooper'],
            'added by': ['Josh', 'Not Josh']
        })
        self.mock_preflight.return_value = preflight_return

        create_return = pd.DataFrame({
            'Username': ['Cooper-Tina@norc.org@test.com'], 'Status': ['Success'], 'SalesforceId': ['005_success'],
            'Error': [None], 'AssignmentErrors': [None]
        })
        self.mock_create_users.return_value = create_return

        mock_args = MagicMock()
        mock_args.input = self.source_excel_path
        mock_args.output = self.output_csv_path
        mock_args.dry_run = False

        handle_provision_workflow(mock_args, self.mock_config)

        self.mock_preflight.assert_called_once()
        self.mock_create_users.assert_called_once()
        self.mock_validate_users.assert_called_once()

        self.assertTrue(os.path.exists(self.output_csv_path))

if __name__ == '__main__':
    unittest.main()
