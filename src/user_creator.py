import pandas as pd
from simple_salesforce.exceptions import SalesforceError

def create_salesforce_users(sf, processed_data, dry_run=True):
    """
    Creates users in Salesforce and assigns permissions.
    Returns a detailed report of the outcome for each user.
    """
    results_list = []

    queue_ids = {}
    if not dry_run:
        all_queue_names = set(
            q_name.strip()
            for queues in processed_data['Queues'].dropna()
            for q_name in queues.split('\n')
            if q_name.strip()
        )
        if all_queue_names:
            in_clause = "('" + "','".join(all_queue_names) + "')"
            query = f"SELECT Id, Name FROM Group WHERE Type = 'Queue' AND Name IN {in_clause}"
            try:
                results = sf.query_all(query)
                for record in results['records']:
                    queue_ids[record['Name']] = record['Id']
            except SalesforceError as e:
                print(f"Warning: Could not query for Queue IDs. {e}")

    for index, user_data in processed_data.iterrows():
        user_identifier = user_data['Username']
        print(f"--- Processing user: {user_identifier} ---")

        result_record = {
            'Username': user_identifier, 'Status': '', 'SalesforceId': None, 'Error': '', 'AssignmentErrors': ''
        }

        user_payload = {
            'Username': user_data['Username'], 'Alias': user_data['Alias'], 'FirstName': user_data['FirstName'],
            'LastName': user_data['LastName'], 'Email': user_data['Email (name version)'], 'ProfileId': user_data['ProfileID'],
            'UserRoleId': user_data['RoleID'], 'TimeZoneSidKey': user_data['TimeZoneSidKey'], 'LocaleSidKey': user_data['LocaleSidKey'],
            'LanguageLocaleKey': user_data['LanguageLocaleKey'], 'EmailEncodingKey': user_data['EmailEncodingKey'],
            'IsActive': user_data['IsActive'],
        }
        if 'UserPermissionsInteractionUser' in user_data and pd.notna(user_data['UserPermissionsInteractionUser']):
             user_payload['UserPermissionsInteractionUser'] = user_data['UserPermissionsInteractionUser']
        if user_data['EnableSSO']:
            user_payload['FederationIdentifier'] = user_data['FederationIdentifier']

        if dry_run:
            print(f"[DRY RUN] Would create user.")
            result_record['Status'] = 'Dry Run - Not Created'
            results_list.append(result_record)
            continue

        try:
            result = sf.User.create(user_payload)
            if not result.get('success', False):
                error_msg = result.get('errors', 'Unknown error')
                # Raise a generic exception to be caught by the outer block
                raise Exception(f"User creation failed: {error_msg}")

            user_id = result['id']
            print(f"Successfully created user with ID: {user_id}")
            result_record.update({'Status': 'Success', 'SalesforceId': user_id})

            assignment_errors = []
            # Assign Permission Set Groups
            if pd.notna(user_data['PermissionSetGroupIDs']):
                for psg_id in str(user_data['PermissionSetGroupIDs']).split(';'):
                    psg_id = psg_id.strip()
                    if not psg_id: continue
                    try:
                        sf.PermissionSetAssignment.create({'AssigneeId': user_id, 'PermissionSetGroupId': psg_id})
                        print(f"Assigned Permission Set Group {psg_id} to user {user_id}")
                    except Exception as e: # Catch any assignment error
                        err_msg = f"Failed to assign Permission Set Group {psg_id}: {e}"
                        print(err_msg)
                        assignment_errors.append(err_msg)

            # Assign to Queues
            if pd.notna(user_data['Queues']):
                for q_name in [q.strip() for q in user_data['Queues'].split('\n') if q.strip()]:
                    if q_name in queue_ids:
                        try:
                            sf.GroupMember.create({'GroupId': queue_ids[q_name], 'UserOrGroupId': user_id})
                            print(f"Assigned user {user_id} to queue {q_name}")
                        except Exception as e: # Catch any assignment error
                            err_msg = f"Failed to assign user to Queue {q_name}: {e}"
                            print(err_msg)
                            assignment_errors.append(err_msg)
                    else:
                        assignment_errors.append(f"Queue '{q_name}' not found.")

            if assignment_errors:
                result_record['Status'] = 'Success with errors'
                result_record['AssignmentErrors'] = "\n".join(assignment_errors)

        except Exception as e: # Catch any error during the process
            print(f"Error processing user {user_identifier}: {e}")
            result_record.update({'Status': 'Failed', 'Error': str(e)})

        results_list.append(result_record)

    return pd.DataFrame(results_list)
