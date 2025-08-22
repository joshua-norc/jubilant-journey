import pandas as pd
from simple_salesforce.exceptions import SalesforceError

def create_salesforce_users(sf, processed_data, dry_run=True):
    """
    Creates users in Salesforce based on the processed data.

    :param sf: The simple-salesforce connection object.
    :param processed_data: The DataFrame with processed user data.
    :param dry_run: If True, prints the actions without executing them.
    """
    # Get Queue IDs from names
    queue_ids = {}
    if not dry_run:
        all_queue_names = set()
        for queues in processed_data['Queues'].dropna():
            for q_name in queues.split('\n'):
                all_queue_names.add(q_name.strip())

        if all_queue_names:
            query = f"SELECT Id, Name FROM Group WHERE Type = 'Queue' AND Name IN {tuple(all_queue_names)}"
            try:
                results = sf.query_all(query)
                for record in results['records']:
                    queue_ids[record['Name']] = record['Id']
            except SalesforceError as e:
                print(f"Error querying for Queue IDs: {e}")


    for index, user_data in processed_data.iterrows():
        user_payload = {
            'Username': user_data['Username'],
            'Alias': user_data['Alias'],
            'FirstName': user_data['FirstName'],
            'LastName': user_data['LastName'],
            'Email': user_data['Email (name version)'],
            'ProfileId': user_data['ProfileID'],
            'UserRoleId': user_data['RoleID'],
            'TimeZoneSidKey': user_data['TimeZoneSidKey'],
            'LocaleSidKey': user_data['LocaleSidKey'],
            'LanguageLocaleKey': user_data['LanguageLocaleKey'],
            'EmailEncodingKey': user_data['EmailEncodingKey'],
            'IsActive': user_data['IsActive'],
        }

        # This field might not be standard on all User objects
        # It's better to check if it exists in the data before adding
        if 'UserPermissionsInteractionUser' in user_data and pd.notna(user_data['UserPermissionsInteractionUser']):
             user_payload['UserPermissionsInteractionUser'] = user_data['UserPermissionsInteractionUser']

        if user_data['EnableSSO']:
            user_payload['FederationIdentifier'] = user_data['FederationIdentifier']

        print(f"--- Processing user: {user_data['Username']} ---")
        if dry_run:
            print(f"[DRY RUN] Would create user with payload: {user_payload}")
            user_id = "DRY_RUN_USER_ID"
        else:
            try:
                print(f"Creating user: {user_data['Username']}")
                result = sf.User.create(user_payload)
                if result.get('success', False):
                    user_id = result['id']
                    print(f"Successfully created user with ID: {user_id}")
                else:
                    print(f"Error creating user: {result.get('errors', 'Unknown error')}")
                    continue
            except SalesforceError as e:
                print(f"Salesforce API error creating user: {e}")
                continue

        # Assign Permission Set Groups
        if pd.notna(user_data['PermissionSetGroupIDs']):
            psg_ids = str(user_data['PermissionSetGroupIDs']).split(';')
            for psg_id in psg_ids:
                psg_id = psg_id.strip()
                if not psg_id: continue

                psg_assignment_payload = {
                    'AssigneeId': user_id,
                    'PermissionSetGroupId': psg_id
                }
                if dry_run:
                    print(f"[DRY RUN] Would assign Permission Set Group: {psg_assignment_payload}")
                else:
                    try:
                        sf.PermissionSetAssignment.create(psg_assignment_payload)
                        print(f"Assigned Permission Set Group {psg_id} to user {user_id}")
                    except SalesforceError as e:
                        print(f"Error assigning Permission Set Group {psg_id}: {e}")

        # Assign to Queues
        if pd.notna(user_data['Queues']):
            queue_names = [q.strip() for q in user_data['Queues'].split('\n')]
            for q_name in queue_names:
                if dry_run:
                    print(f"[DRY RUN] Would assign user to queue: {q_name}")
                elif q_name in queue_ids:
                    group_member_payload = {
                        'GroupId': queue_ids[q_name],
                        'UserOrGroupId': user_id
                    }
                    try:
                        sf.GroupMember.create(group_member_payload)
                        print(f"Assigned user {user_id} to queue {q_name}")
                    except SalesforceError as e:
                        print(f"Error assigning user to queue {q_name}: {e}")
                else:
                    print(f"Could not find Queue ID for queue: {q_name}")


if __name__ == '__main__':
    print("This module provides functions for user creation and configuration. It is not meant to be run directly.")
