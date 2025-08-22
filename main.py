import argparse
import configparser
import os
import pandas as pd
from src.salesforce_client import SalesforceClient
from src.data_processor import process_dataframes
from src.user_creator import create_salesforce_users
from src.reporter import validate_created_users
from src.preflight import run_duplicate_check
import src.org_analyzer as analyzer

def handle_provision(args, config):
    """Handles the user provisioning process."""
    if not (os.path.isfile(args.input) and args.input.endswith('.xlsx')):
        print(f"Error: Input '{args.input}' must be an Excel (.xlsx) file for the provision command.")
        return

    try:
        settings = config['settings']
        environment = settings.get('environment', 'Training')
    except KeyError:
        print("Error: [settings] section not found in config.ini.")
        return

    print(f"--- Starting User Provisioning ---")
    print(f"Environment: {environment}, Input File: {args.input}, Dry Run: {args.dry_run}")

    try:
        excel_file = pd.ExcelFile(args.input)
        user_df = excel_file.read('Users2Add')
        persona_df = excel_file.read('Persona Mapping')
        sso_df = excel_file.read('TSSO_TrainTheTrainer')
    except Exception as e:
        print(f"An error occurred while loading data from Excel file: {e}")
        return

    sf_connection = connect_to_salesforce(config)
    if not sf_connection: return

    preflight_report = run_duplicate_check(sf_connection, user_df)

    users_to_create_df = preflight_report[preflight_report['Action'] == 'Create New User'].copy()

    creation_results_df = pd.DataFrame()
    if not users_to_create_df.empty:
        print(f"\nProceeding to create {len(users_to_create_df)} new users.")
        processed_data = process_dataframes(users_to_create_df, persona_df, sso_df, environment)
        creation_results_df = create_salesforce_users(sf_connection, processed_data, args.dry_run)
    else:
        print("\nNo new users to create after pre-flight check.")

    if not creation_results_df.empty:
        preflight_report = preflight_report.merge(
            creation_results_df[['Username', 'Status', 'Error', 'SalesforceId', 'AssignmentErrors']],
            on='Username',
            how='left'
        )
        preflight_report['Status'].fillna('Skipped', inplace=True)

        # Final validation call
        if not args.dry_run:
            successful_ids = list(creation_results_df[creation_results_df['Status'] == 'Success']['SalesforceId'].dropna())
            validate_created_users(sf_connection, successful_ids)

    print(f"\nWriting results back to {args.input}...")
    try:
        with pd.ExcelWriter(args.input, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
            preflight_report.to_excel(writer, sheet_name='preflight', index=False)

            if not creation_results_df.empty and not args.dry_run:
                users_created_df = creation_results_df[creation_results_df['Status'].str.startswith('Success')]
                users_created_df.to_excel(writer, sheet_name='UsersCreated', index=False)
        print("Successfully wrote 'preflight' and 'UsersCreated' sheets.")
    except Exception as e:
        print(f"Error writing to Excel file: {e}")

    print("\n--- User Provisioning Finished ---")


def handle_report(args, config):
    # ... (this function remains the same)
    pass


def connect_to_salesforce(config):
    # ... (this function remains the same)
    pass

def main():
    # ... (this function remains the same)
    pass

if __name__ == '__main__':
    # ... (this function remains the same)
    pass
