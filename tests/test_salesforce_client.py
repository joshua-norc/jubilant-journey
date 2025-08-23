import unittest
from unittest.mock import patch
import configparser
from src.salesforce_client import SalesforceClient

class TestSalesforceClient(unittest.TestCase):

    @patch('src.salesforce_client.Salesforce')
    def test_password_auth(self, mock_salesforce_class):
        """Test that the client initializes with password authentication."""
        config = configparser.ConfigParser()
        config['salesforce_creds'] = {
            'username': 'testuser',
            'password': 'testpassword',
            'security_token': 'testtoken'
        }

        client = SalesforceClient(config)
        client.connect()

        mock_salesforce_class.assert_called_once_with(
            username='testuser',
            password='testpassword',
            security_token='testtoken'
        )

    @patch('src.salesforce_client.Salesforce')
    def test_jwt_auth(self, mock_salesforce_class):
        """Test that the client initializes with JWT authentication."""
        config = configparser.ConfigParser()
        config['salesforce_creds'] = {
            'username': 'testuser',
            'private_key_file': 'path/to/key.pem',
            'consumer_key': 'testconsumerkey'
        }

        client = SalesforceClient(config)
        client.connect()

        mock_salesforce_class.assert_called_once_with(
            username='testuser',
            consumer_key='testconsumerkey',
            privatekey_file='path/to/key.pem'
        )

    def test_invalid_config_missing_all(self):
        """Test that a ValueError is raised for incomplete configuration."""
        config = configparser.ConfigParser()
        config['salesforce_creds'] = {
            'username': 'testuser' # Incomplete
        }

        with self.assertRaisesRegex(ValueError, "Salesforce credentials are not fully set"):
            SalesforceClient(config)

    def test_invalid_config_missing_jwt_user(self):
        """Test that a ValueError is raised for JWT auth without a username."""
        config = configparser.ConfigParser()
        config['salesforce_creds'] = {
            'private_key_file': 'path/to/key.pem',
            'consumer_key': 'testconsumerkey'
        }

        with self.assertRaisesRegex(ValueError, "'username' is required for JWT"):
            SalesforceClient(config)


    @patch('src.salesforce_client.Salesforce')
    def test_password_auth_with_domain(self, mock_salesforce_class):
        """Test password auth with the domain parameter for sandboxes."""
        config = configparser.ConfigParser()
        config['salesforce_creds'] = {
            'username': 'testuser',
            'password': 'testpassword',
            'security_token': 'testtoken',
            'domain': 'test'
        }

        client = SalesforceClient(config)
        client.connect()

        # Check that instance_url is NOT passed when domain is present
        mock_salesforce_class.assert_called_once_with(
            username='testuser',
            password='testpassword',
            security_token='testtoken',
            domain='test'
        )

if __name__ == '__main__':
    unittest.main()
