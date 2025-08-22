import configparser
from simple_salesforce import Salesforce

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
            self.username = self.config.get('username') # username is also needed for JWT
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
        except Exception as e:
            print(f"Failed to connect to Salesforce: {e}")
            self.sf = None
        return self.sf

if __name__ == '__main__':
    # Example usage:
    # 1. Create a config.ini file from the config.ini.example template
    # 2. Fill in your credentials

    config = configparser.ConfigParser()
    # In a real run, this would be 'config.ini'
    if not config.read('config.ini.example'):
        print("Could not read config file. Make sure 'config.ini.example' exists.")
    else:
        try:
            # Note: This example will fail if you use the placeholder values.
            client = SalesforceClient(config)
            sf_connection = client.connect()

            if sf_connection:
                print("Salesforce connection is live.")
        except ValueError as e:
            print(f"Configuration Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
