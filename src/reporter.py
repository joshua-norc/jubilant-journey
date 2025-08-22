import pandas as pd
import os
from datetime import datetime
from simple_salesforce.exceptions import SalesforceError

def generate_report(sf, user_ids):
    """
    Generates a CSV report of newly created users.

    :param sf: The simple-salesforce connection object.
    :param user_ids: A list of IDs of the newly created users.
    """
    if not user_ids:
        print("No users were created, so no report will be generated.")
        return

    print(f"Generating report for {len(user_ids)} newly created users...")

    # SOQL query to get details of the created users
    # We need to format the list of IDs into a string for the IN clause
    id_list_str = "('" + "','".join(user_ids) + "')"
    query = f"""
    SELECT Id, Username, Name, Email, Profile.Name, UserRole.Name, FederationIdentifier, IsActive
    FROM User
    WHERE Id IN {id_list_str}
    """

    try:
        results = sf.query_all(query)
        records = results['records']

        # The API might return an OrderedDict, so we convert it to a list of dicts
        processed_records = []
        for record in records:
            rec_dict = dict(record)
            if 'attributes' in rec_dict:
                del rec_dict['attributes']
            # Flatten nested records for Profile and UserRole
            if rec_dict.get('Profile'):
                rec_dict['ProfileName'] = rec_dict['Profile']['Name']
                del rec_dict['Profile']
            else:
                rec_dict['ProfileName'] = None
            if rec_dict.get('UserRole'):
                rec_dict['UserRoleName'] = rec_dict['UserRole']['Name']
                del rec_dict['UserRole']
            else:
                rec_dict['UserRoleName'] = None
            processed_records.append(rec_dict)

        # Convert to DataFrame
        report_df = pd.DataFrame(processed_records)

        # Ensure reports directory exists
        if not os.path.exists('reports'):
            os.makedirs('reports')

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"user_creation_report_{timestamp}.csv"
        report_path = os.path.join('reports', report_filename)

        # Save report
        report_df.to_csv(report_path, index=False)
        print(f"Report successfully generated at: {report_path}")

    except SalesforceError as e:
        print(f"Error querying Salesforce for report data: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during report generation: {e}")

if __name__ == '__main__':
    print("This module provides functions for generating reports. It is not meant to be run directly.")
