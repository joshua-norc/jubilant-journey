import unittest
import pandas as pd
import os
import tempfile
from src.data_processor import load_and_process_data

class TestDataProcessor(unittest.TestCase):

    def setUp(self):
        """Set up temporary directory and dummy CSV files for tests."""
        self.test_dir = tempfile.TemporaryDirectory()

        self.training_template_path = os.path.join(self.test_dir.name, "training.csv")
        self.persona_mapping_path = os.path.join(self.test_dir.name, "persona.csv")
        self.tsso_path = os.path.join(self.test_dir.name, "sso.csv")

        # Create dummy data
        training_data = {
            'Email (employee ID version)': ['user1@test.com', 'user2@test.com'],
            'FirstName': ['Test', 'User'],
            'LastName': ['One', 'Two'],
            'Persona Name': ['Test Persona 1', 'Test Persona 2'],
            'Username': ['user1', 'user2'],
            'Alias': ['u1', 'u2'],
            'IsActive': [True, True],
            'TimeZoneSidKey': ['America/New_York', 'America/Los_Angeles'],
            'LocaleSidKey': ['en_US', 'en_US'],
            'ProfileId': ['p1', 'p2'],
            'UserType': ['Standard', 'Standard'],
            'LanguageLocaleKey': ['en_US', 'en_US'],
            'Call Center': ['cc1', 'cc2'],
            'FederationIdentifier': ['fed1', 'fed2'],
            'Is_Migrated__c': [False, False],
            'UserPermissionsInteractionUser': [True, False],
            'EmailEncodingKey': ['UTF-8', 'UTF-8'],
            'Training User ID': ['tid1', 'tid2']
        }
        pd.DataFrame(training_data).to_csv(self.training_template_path, index=False)

        persona_data = {
            'Persona Name': ['Test Persona 1', 'Test Persona 2'],
            'Profile ID (Training)': ['prof_train_1', 'prof_train_2'],
            'Role ID (Training)': ['role_train_1', 'role_train_2'],
            'Permission Set Group IDs (Training)': ['psg_train_1', 'psg_train_2'],
            'Contact Center Training': ['cc_train_1', 'cc_train_2'],
            'Profile ID (Prod)': ['prof_prod_1', 'prof_prod_2'],
            'Role ID (Prod)': ['role_prod_1', 'role_prod_2'],
            'Permission Set Group IDs (Prod)': ['psg_prod_1', 'psg_prod_2'],
            'Contact Center Prod': ['cc_prod_1', 'cc_prod_2'],
            'Queues': ['Queue1\nQueue2', 'Queue3']
        }
        pd.DataFrame(persona_data).to_csv(self.persona_mapping_path, index=False)

        sso_data = {
            'Email (employee ID version)': ['user1@test.com']
        }
        pd.DataFrame(sso_data).to_csv(self.tsso_path, index=False)

    def tearDown(self):
        """Clean up the temporary directory."""
        self.test_dir.cleanup()

    def test_successful_processing_training_env(self):
        """Test successful data processing for the Training environment."""
        df = load_and_process_data(self.training_template_path, self.persona_mapping_path, self.tsso_path, environment='Training')
        self.assertIsNotNone(df)
        self.assertEqual(len(df), 2)
        self.assertTrue('EnableSSO' in df.columns)
        self.assertEqual(df[df['Email (employee ID version)'] == 'user1@test.com']['EnableSSO'].iloc[0], True)
        self.assertEqual(df[df['Email (employee ID version)'] == 'user2@test.com']['EnableSSO'].iloc[0], False)
        self.assertEqual(df.iloc[0]['ProfileID'], 'prof_train_1')

    def test_successful_processing_prod_env(self):
        """Test successful data processing for the Prod environment."""
        df = load_and_process_data(self.training_template_path, self.persona_mapping_path, self.tsso_path, environment='Prod')
        self.assertIsNotNone(df)
        self.assertEqual(df.iloc[0]['ProfileID'], 'prof_prod_1')

    def test_file_not_found(self):
        """Test that None is returned when a file is not found."""
        df = load_and_process_data("nonexistent.csv", self.persona_mapping_path, self.tsso_path)
        self.assertIsNone(df)

    def test_missing_environment_column(self):
        """Test that a ValueError is raised for a missing environment column."""
        with self.assertRaises(ValueError):
            load_and_process_data(self.training_template_path, self.persona_mapping_path, self.tsso_path, environment='QA2')

if __name__ == '__main__':
    unittest.main()
