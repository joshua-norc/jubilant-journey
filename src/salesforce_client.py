import configparser
from simple_salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceAuthenticationFailed

class SalesforceClient:
    """
    A client to connect to the Salesforce API using settings from a config file.
    """
    def __init__(self, config: configparser.ConfigParser):
        """
        Initializes the SalesforceClient.
        Reads credentials from the provided config object.
        """
        self.config = config['salesforce_creds']
        self.sf = None
        self.auth_method = None

        # Determine authentication method
        if self.config.get('private_key_file') and self.config.get('consumer_key'):
            self.auth_method = 'jwt'
            self.private_key_file = self.config['private_key_file']
            self.consumer_key = self.config['consumer_key']
            self.username = self.config.get('username')
            if not self.username:
                 raise ValueError("'username' is required for JWT Bearer Flow authentication.")
        elif self.config.get('username') and self.config.get('password') and self.config.get('security_token'):
            self.auth_method = 'password'
            self.username = self.config['username']
            self.password = self.config['password']
            self.security_token = self.config['security_token']
            self.instance_url = self.config.get('instance_url', 'login.salesforce.com')
        else:
            raise ValueError("Salesforce credentials are not fully set in config file. Provide either username/password/token or private_key_file/consumer_key.")

    def connect(self):
        """
        Connects to Salesforce using the determined authentication method.
        """
        try:
            print(f"Attempting to connect to Salesforce using {self.auth_method} authentication...")
            if self.auth_method == 'jwt':
                self.sf = Salesforce(
                    username=self.username,
                    consumer_key=self.consumer_key,
                    privatekey_file=self.private_key_file
                )
            elif self.auth_method == 'password':
                self.sf = Salesforce(
                    username=self.username,
                    password=self.password,
                    security_token=self.security_token,
                    instance_url=self.instance_url
                )
            print("Successfully connected to Salesforce.")
        except SalesforceAuthenticationFailed as e:
            print("\n--- Salesforce Authentication Failed ---")
            print(f"Error: {e.content[0]['message']} (ErrorCode: {e.content[0]['errorCode']})")
            print("\nPlease check the following:")
            print("1. Your username, password, and security token are correct.")
            print("2. If connecting to a sandbox, ensure 'instance_url' in config.ini is set to 'test.salesforce.com'.")
            print("3. Your organization's IP restrictions are not blocking your IP address.")
            self.sf = None
        except Exception as e:
            print(f"An unexpected error occurred during connection: {e}")
            self.sf = None
        return self.sf

if __name__ == '__main__':
    # This module is not meant to be run directly.
    pass
