import pandas as pd
from simple_salesforce.exceptions import SalesforceError

def get_users_by_permission_set(sf, permission_set_name):
    """Queries for users assigned to a specific permission set."""
    print(f"Querying for users with permission set: {permission_set_name}...")
    query = f"""
    SELECT Assignee.Name, Assignee.Email, Assignee.Profile.Name
    FROM PermissionSetAssignment
    WHERE PermissionSet.Name = '{permission_set_name}'
    ORDER BY Assignee.Name
    """
    try:
        results = sf.query_all(query)
        return pd.DataFrame(results['records'])
    except SalesforceError as e:
        print(f"Salesforce API error: {e}")
        return None

def list_permissions_by_modified_date(sf):
    """Queries for permission sets sorted by last modified date."""
    print("Querying for permission sets by last modified date...")
    query = "SELECT Name, LastModifiedDate FROM PermissionSet ORDER BY LastModifiedDate DESC"
    try:
        results = sf.query_all(query)
        return pd.DataFrame(results['records'])
    except SalesforceError as e:
        print(f"Salesforce API error: {e}")
        return None

def list_connected_apps(sf):
    """Queries for all connected apps."""
    print("Querying for all connected apps...")
    query = "SELECT Name, LastModifiedDate FROM ConnectedApp ORDER BY LastModifiedDate DESC"
    try:
        results = sf.query_all(query)
        return pd.DataFrame(results['records'])
    except SalesforceError as e:
        print(f"Salesforce API error: {e}")
        return None

def get_connected_app_details(sf, app_name):
    """Gets detailed information about a specific connected app."""
    print(f"Querying for details of connected app: {app_name}...")
    # This is a complex query and might require multiple API calls.
    # For now, we'll get the main details.
    # Finding users and installer is not available through a simple SOQL query.
    # This would require more advanced use of the APIs or parsing the audit trail.
    query = f"SELECT Name, DeveloperName, StartUrl, MobileStartUrl FROM ConnectedApp WHERE Name = '{app_name}'"
    try:
        results = sf.query(query)
        if results['totalSize'] > 0:
            return pd.DataFrame(results['records'])
        else:
            print(f"No connected app found with name: {app_name}")
            return None
    except SalesforceError as e:
        print(f"Salesforce API error: {e}")
        return None

if __name__ == '__main__':
    print("This module provides functions for analyzing a Salesforce org. It is not meant to be run directly.")
