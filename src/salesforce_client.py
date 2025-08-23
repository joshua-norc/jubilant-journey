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
        self.creds = config['salesforce_creds']
        self.sf = None
        self.auth_method = None
        self.connection_params = {}

        # Determine authentication method
        if self.creds.get('private_key_file') and self.creds.get('consumer_key'):
            self.auth_method = 'jwt'
            self.connection_params = {
                'username': self.creds.get('username'),
                'consumer_key': self.creds.get('consumer_key'),
                'privatekey_file': self.creds.get('private_key_file')
            }
            if not self.connection_params['username']:
                 raise ValueError("'username' is required for JWT Bearer Flow authentication.")
        elif self.creds.get('username') and self.creds.get('password') and self.creds.get('security_token'):
            self.auth_method = 'password'
            self.connection_params = {
                'username': self.creds.get('username'),
                'password': self.creds.get('password'),
                'security_token': self.creds.get('security_token'),
                'instance_url': self.creds.get('instance_url'),
                'domain': self.creds.get('domain')
            }
            # simple-salesforce prefers domain for sandboxes, so we remove instance_url if domain is present
            if self.connection_params['domain']:
                self.connection_params['instance_url'] = None
        else:
            raise ValueError("Salesforce credentials are not fully set in config file.")

    def connect(self):
        """
        Connects to Salesforce using the determined authentication method.
        """
        # Filter out None values from connection params
        active_params = {k: v for k, v in self.connection_params.items() if v is not None}

        # Prepare params for logging (masking secrets)
        logging_params = active_params.copy()
        if 'password' in logging_params:
            logging_params['password'] = '********'
        if 'security_token' in logging_params:
            logging_params['security_token'] = '********'

        print(f"Attempting to connect to Salesforce using '{self.auth_method}' auth with params: {logging_params}")

        try:
            self.sf = Salesforce(**active_params)
            print("Successfully connected to Salesforce.")
        except SalesforceAuthenticationFailed as e:
            print("\n--- Salesforce Authentication Failed ---")
            print(f"Error: {e.content[0]['message']} (ErrorCode: {e.content[0]['errorCode']})")
            print("\nPlease check the following:")
            print("1. Your username, password, and security token are correct.")
            print("2. If connecting to a sandbox, try setting 'domain = test' in your config.ini.")
            print("3. If using a custom domain, ensure 'instance_url' is set correctly (e.g., 'https://your-domain.my.salesforce.com').")
            print("4. Your organization's IP restrictions are not blocking your IP address.")
            self.sf = None
        except Exception as e:
            print(f"An unexpected error occurred during connection: {e}")
            self.sf = None
        return self.sf
