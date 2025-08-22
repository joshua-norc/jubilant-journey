import pandas as pd
from simple_salesforce.exceptions import SalesforceError

def run_duplicate_check(sf, users_to_add_df):
    """
    Checks for duplicate users in Salesforce before attempting to create new ones.

    :param sf: The simple-salesforce connection object.
    :param users_to_add_df: DataFrame of users to be added.
    :return: A DataFrame (preflight report) with 'Action' and 'Notes' columns.
    """
    print("--- Starting Pre-flight Duplicate Check ---")

    # Make a copy to avoid modifying the original dataframe
    preflight_report = users_to_add_df.copy()
    preflight_report['Action'] = 'Create New User'
    preflight_report['Notes'] = ''

    # Get lists of emails and usernames for querying
    emails_to_check = list(preflight_report['Email (name version)'].dropna().unique())
    usernames_to_check = list(preflight_report['Username'].dropna().unique())

    existing_users = {}

    # Query for existing users by email or username
    if emails_to_check or usernames_to_check:
        # Combine checks into one query for efficiency
        where_clauses = []
        if emails_to_check:
            where_clauses.append(f"Email IN ('{ "','".join(emails_to_check) }')")
        if usernames_to_check:
            where_clauses.append(f"Username IN ('{ "','".join(usernames_to_check) }')")

        full_where_clause = " OR ".join(where_clauses)

        query = f"SELECT Id, Email, Username, Name FROM User WHERE {full_where_clause}"

        try:
            results = sf.query_all(query)
            for record in results['records']:
                if record.get('Email'):
                    existing_users[record['Email'].lower()] = {'Id': record['Id'], 'Note': f"Email match on User ID {record['Id']}"}
                if record.get('Username'):
                    existing_users[record['Username'].lower()] = {'Id': record['Id'], 'Note': f"Username match on User ID {record['Id']}"}
        except SalesforceError as e:
            print(f"Warning: Could not query for duplicate users. {e}")

    # Check for duplicates and update the report
    for index, row in preflight_report.iterrows():
        email_lower = str(row['Email (name version)']).lower()
        username_lower = str(row['Username']).lower()

        if email_lower in existing_users:
            preflight_report.loc[index, 'Action'] = 'Skip - Duplicate Found'
            preflight_report.loc[index, 'Notes'] = existing_users[email_lower]['Note']
        elif username_lower in existing_users:
            preflight_report.loc[index, 'Action'] = 'Skip - Duplicate Found'
            preflight_report.loc[index, 'Notes'] = existing_users[username_lower]['Note']

    print("--- Pre-flight Duplicate Check Finished ---")
    skipped_count = len(preflight_report[preflight_report['Action'] != 'Create New User'])
    print(f"Found {skipped_count} potential duplicates. See 'preflight' sheet for details.")

    return preflight_report


if __name__ == '__main__':
    print("This module provides functions for pre-flight checks. It is not meant to be run directly.")
