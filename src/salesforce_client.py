import os
from simple_salesforce import Salesforce

class SalesforceClient:
    """
    A client to connect to the Salesforce API.
    """
    def __init__(self):
        """
        Initializes the SalesforceClient.
        Credentials are expected to be set as environment variables:
        - SF_USERNAME
        - SF_PASSWORD
        - SF_SECURITY_TOKEN
        - SF_INSTANCE_URL (e.g., 'login.salesforce.com' for production)
        """
        self.username = os.getenv("SF_USERNAME")
        self.password = os.getenv("SF_PASSWORD")
        self.security_token = os.getenv("SF_SECURITY_TOKEN")
        self.instance_url = os.getenv("SF_INSTANCE_URL")
        self.sf = None

        if not all([self.username, self.password, self.security_token, self.instance_url]):
            raise ValueError("Salesforce credentials are not fully set in environment variables. Please set SF_USERNAME, SF_PASSWORD, SF_SECURITY_TOKEN, and SF_INSTANCE_URL.")

    def connect(self):
        """
        Connects to Salesforce.
        """
        try:
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
    # Set up your environment variables before running this.
    # In your terminal, run the following commands:
    # export SF_USERNAME='your_username'
    # export SF_PASSWORD='your_password'
    # export SF_SECURITY_TOKEN='your_token'
    # export SF_INSTANCE_URL='login.salesforce.com'

    try:
        client = SalesforceClient()
        sf_connection = client.connect()

        if sf_connection:
            print("Salesforce connection is live.")
            # You can now use sf_connection to interact with Salesforce
            # For example, to query some data:
            # data = sf_connection.query("SELECT Id, Name FROM Account LIMIT 5")
            # print(data)
    except ValueError as e:
        print(e)
