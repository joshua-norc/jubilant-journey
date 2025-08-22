import pandas as pd

def load_and_process_data(training_template_path, persona_mapping_path, tsso_path, environment='Training'):
    """
    Loads data from CSV files, processes it, and merges it.

    :param training_template_path: Path to the training template CSV.
    :param persona_mapping_path: Path to the persona mapping CSV.
    :param tsso_path: Path to the TSSO users CSV.
    :param environment: The target Salesforce environment ('QA2', 'Training', or 'Prod').
    :return: A pandas DataFrame with the processed user data.
    """
    # Load the CSV files
    try:
        user_data = pd.read_csv(training_template_path)
        persona_mapping = pd.read_csv(persona_mapping_path)
        sso_users = pd.read_csv(tsso_path)
    except FileNotFoundError as e:
        print(f"Error loading data files: {e}")
        return None

    # Select the correct columns from persona_mapping based on the environment
    env_specific_columns = {
        'ProfileID': f'Profile ID ({environment})',
        'RoleID': f'Role ID ({environment})',
        'PermissionSetGroupIDs': f'Permission Set Group IDs ({environment})',
        'ContactCenterID': f'Contact Center {environment}'
    }

    # Check if the environment-specific columns exist
    for col in env_specific_columns.values():
        if col not in persona_mapping.columns:
            raise ValueError(f"Column '{col}' not found in persona mapping file for environment '{environment}'.")

    # Create a copy to avoid SettingWithCopyWarning
    persona_mapping_env = persona_mapping[['Persona Name', 'Queues'] + list(env_specific_columns.values())].copy()

    # Rename columns for merging
    persona_mapping_env.rename(columns={v: k for k, v in env_specific_columns.items()}, inplace=True)

    # Merge user data with persona mapping
    # Using 'Persona Name' from user_data and persona_mapping_env
    processed_data = pd.merge(user_data, persona_mapping_env, on='Persona Name', how='left')

    # Identify SSO users
    sso_user_emails = sso_users['Email (employee ID version)']
    processed_data['EnableSSO'] = processed_data['Email (employee ID version)'].isin(sso_user_emails)

    return processed_data

if __name__ == '__main__':
    # Example usage:
    training_file = 'data/training_template.csv'
    persona_file = 'data/persona_mapping.csv'
    sso_file = 'data/tsso_trainthetrainer.csv'

    # Process for the 'Training' environment
    try:
        final_user_data = load_and_process_data(training_file, persona_file, sso_file, environment='Training')

        if final_user_data is not None:
            print("Processed data:")
            print(final_user_data.head().to_string())
            print("\nColumns:")
            print(final_user_data.columns)
            print("\nSSO Enabled for:")
            print(final_user_data[final_user_data['EnableSSO']].to_string())
    except ValueError as e:
        print(e)
