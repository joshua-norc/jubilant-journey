import pandas as pd

def process_dataframes(user_df, persona_df, sso_df, environment='Training'):
    """
    Processes pre-loaded DataFrames of user data, merging and adding SSO info.

    :param user_df: DataFrame with the core user data.
    :param persona_df: DataFrame with the persona to permission mappings.
    :param sso_df: DataFrame listing users who require SSO.
    :param environment: The target Salesforce environment ('QA2', 'Training', or 'Prod').
    :return: A pandas DataFrame with the processed user data.
    """
    # Select the correct columns from persona_mapping based on the environment
    env_specific_columns = {
        'ProfileID': f'Profile ID ({environment})',
        'RoleID': f'Role ID ({environment})',
        'PermissionSetGroupIDs': f'Permission Set Group IDs ({environment})',
        'ContactCenterID': f'Contact Center {environment}'
    }

    # Check if the environment-specific columns exist
    for col in env_specific_columns.values():
        if col not in persona_df.columns:
            raise ValueError(f"Column '{col}' not found in persona mapping file for environment '{environment}'.")

    # Create a copy to avoid SettingWithCopyWarning
    persona_mapping_env = persona_df[['Persona Name', 'Queues'] + list(env_specific_columns.values())].copy()

    # Rename columns for merging
    persona_mapping_env.rename(columns={v: k for k, v in env_specific_columns.items()}, inplace=True)

    # Merge user data with persona mapping
    processed_data = pd.merge(user_df, persona_mapping_env, on='Persona Name', how='left')

    # Identify SSO users
    sso_user_emails = sso_df['Email (employee ID version)']
    processed_data['EnableSSO'] = processed_data['Email (employee ID version)'].isin(sso_user_emails)

    return processed_data


def load_and_process_csv_data(training_template_path, persona_mapping_path, tsso_path, environment='Training'):
    """
    Loads data from CSV files, then processes it.

    :param training_template_path: Path to the training template CSV.
    :param persona_mapping_path: Path to the persona mapping CSV.
    :param tsso_path: Path to the TSSO users CSV.
    :param environment: The target Salesforce environment.
    :return: A pandas DataFrame with the processed user data.
    """
    try:
        user_data = pd.read_csv(training_template_path)
        persona_mapping = pd.read_csv(persona_mapping_path)
        sso_users = pd.read_csv(tsso_path)
    except FileNotFoundError as e:
        print(f"Error loading data files: {e}")
        return None

    return process_dataframes(user_data, persona_mapping, sso_users, environment)

if __name__ == '__main__':
    # This module is not meant to be run directly anymore.
    # The main script will handle loading data and calling process_dataframes.
    print("This module provides functions for processing user data. It is not meant to be run directly.")
