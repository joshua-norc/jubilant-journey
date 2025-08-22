import pandas as pd
from simple_salesforce.exceptions import SalesforceError
from src.mapper import map_row_to_payload

def create_salesforce_users(sf, processed_data, mapping, dry_run=True):
    """
    Creates users in Salesforce using a dynamic mapping.
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
        user_identifier = user_data.get('Username', f"Row_{index}")
        print(f"--- Processing user: {user_identifier} ---")

        result_record = {
            'Username': user_identifier, 'Status': '', 'SalesforceId': None, 'Error': '', 'AssignmentErrors': ''
        }

        # Use the mapper to create the payload
        user_payload = map_row_to_payload(user_data, mapping)

        # Add fields from the processed data that are not in the mapping file
        if 'ProfileID' in user_data and pd.notna(user_data['ProfileID']):
             user_payload['ProfileId'] = user_data['ProfileID']
        if 'RoleID' in user_data and pd.notna(user_data['RoleID']):
             user_payload['UserRoleId'] = user_data['RoleID']
        if 'EnableSSO' in user_data and user_data['EnableSSO'] and 'FederationIdentifier' not in user_payload:
            # If SSO is enabled but FederationIdentifier was not in the mapping, use a default
            if 'FederationIdentifier' in user_data and pd.notna(user_data['FederationIdentifier']):
                user_payload['FederationIdentifier'] = user_data['FederationIdentifier']


        if dry_run:
            print(f"[DRY RUN] Would create user with payload: {user_payload}")
            result_record['Status'] = 'Dry Run - Not Created'
            results_list.append(result_record)
            continue

        try:
            result = sf.User.create(user_payload)
            if not result.get('success', False):
                raise Exception(f"User creation failed: {result.get('errors', 'Unknown error')}")

            user_id = result['id']
            print(f"Successfully created user with ID: {user_id}")
            result_record.update({'Status': 'Success', 'SalesforceId': user_id})

            assignment_errors = []
            # Assign Permission Set Groups
            if 'PermissionSetGroupIDs' in user_data and pd.notna(user_data['PermissionSetGroupIDs']):
                for psg_id in str(user_data['PermissionSetGroupIDs']).split(';'):
                    psg_id = psg_id.strip()
                    if not psg_id: continue
                    try:
                        sf.PermissionSetAssignment.create({'AssigneeId': user_id, 'PermissionSetGroupId': psg_id})
                        print(f"Assigned Permission Set Group {psg_id} to user {user_id}")
                    except Exception as e:
                        err_msg = f"Failed to assign PSG {psg_id}: {e}"
                        print(err_msg)
                        assignment_errors.append(err_msg)

            # Assign to Queues
            if 'Queues' in user_data and pd.notna(user_data['Queues']):
                for q_name in [q.strip() for q in user_data['Queues'].split('\n') if q.strip()]:
                    if q_name in queue_ids:
                        try:
                            sf.GroupMember.create({'GroupId': queue_ids[q_name], 'UserOrGroupId': user_id})
                            print(f"Assigned user {user_id} to queue {q_name}")
                        except Exception as e:
                            err_msg = f"Failed to assign to Queue {q_name}: {e}"
                            print(err_msg)
                            assignment_errors.append(err_msg)
                    else:
                        assignment_errors.append(f"Queue '{q_name}' not found.")

            if assignment_errors:
                result_record['Status'] = 'Success with errors'
                result_record['AssignmentErrors'] = "\n".join(assignment_errors)

        except Exception as e:
            print(f"Error processing user {user_identifier}: {e}")
            result_record.update({'Status': 'Failed', 'Error': str(e)})

        results_list.append(result_record)

    return pd.DataFrame(results_list)
