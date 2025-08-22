import argparse
import configparser
import os
import pandas as pd
from src.salesforce_client import SalesforceClient
from src.data_processor import process_dataframes
from src.user_creator import create_salesforce_users
from src.reporter import validate_created_users
from src.preflight import run_duplicate_check
from src.mapper import load_mapping

def handle_preflight(args, config):
    """Runs the pre-flight duplicate check and saves the report."""
    print("--- Running Pre-flight Check ---")
    if not (os.path.isfile(args.input) and args.input.endswith('.xlsx')):
        print(f"Error: Input '{args.input}' must be an Excel (.xlsx) file.")
        return

    sf_connection = connect_to_salesforce(config)
    if not sf_connection: return

    try:
        user_df = pd.read_excel(args.input, sheet_name='Training Template')
    except Exception as e:
        print(f"Error reading 'Training Template' sheet from {args.input}: {e}")
        return

    preflight_report = run_duplicate_check(sf_connection, user_df)

    try:
        preflight_report.to_csv(args.output, index=False)
        print(f"Pre-flight report saved to: {args.output}")
    except Exception as e:
        print(f"Error saving pre-flight report to {args.output}: {e}")

def handle_create_users(args, config):
    """Creates users based on a pre-flight report."""
    print("--- Running User Creation ---")
    settings = config['settings']
    mapping_file = settings.get('mapping_file')
    if not mapping_file or not os.path.isfile(mapping_file):
        print(f"Error: Mapping file '{mapping_file}' not found or not specified in config.ini.")
        return

    mapping = load_mapping(mapping_file)
    if not mapping: return

    try:
        preflight_df = pd.read_csv(args.input)
        excel_file = pd.ExcelFile(args.excel_source)
        persona_df = excel_file.parse('Persona Mapping')
        sso_df = excel_file.parse('TSSO_TrainTheTrainer')
        environment = settings.get('environment', 'Training')
    except Exception as e:
        print(f"Error loading required data: {e}")
        return

    sf_connection = connect_to_salesforce(config)
    if not sf_connection: return

    users_to_create_df = preflight_df[preflight_df['Action'] == 'Create New User'].copy()
    if users_to_create_df.empty:
        print("No new users to create based on the pre-flight report.")
        return

    processed_data = process_dataframes(users_to_create_df, persona_df, sso_df, environment)
    creation_results_df = create_salesforce_users(sf_connection, processed_data, mapping, args.dry_run)

    try:
        creation_results_df.to_csv(args.output, index=False)
        print(f"Creation results saved to: {args.output}")
    except Exception as e:
        print(f"Error saving creation results to {args.output}: {e}")

def handle_validate(args, config):
    """Validates created users."""
    print("--- Running Validation ---")
    try:
        results_df = pd.read_csv(args.input)
        source_df = pd.read_excel(args.excel_source, sheet_name='Training Template')

        # We need a common key to merge on, 'Username' is a good candidate if it's in both files.
        # Let's assume the results_df from user_creator contains the original username.
        validation_data = pd.merge(results_df, source_df, on='Username', how='left')

        successful_users = validation_data[validation_data['Status'] == 'Success']

        # Check if the 'added by' column exists before filtering
        if 'added by' in successful_users.columns:
            users_to_validate = successful_users[successful_users['added by'] == 'Josh']
        else:
            print("Warning: 'added by' column not found in 'Training Template' sheet. Validating all successful users.")
            users_to_validate = successful_users

        if users_to_validate.empty:
            print("No users to validate based on the criteria.")
            return

        ids_to_validate = list(users_to_validate['SalesforceId'].dropna())
        if not ids_to_validate:
            print("No valid Salesforce IDs to query for validation.")
            return

    except Exception as e:
        print(f"Error loading or processing files for validation: {e}")
        return

    sf_connection = connect_to_salesforce(config)
    if not sf_connection: return

    validate_created_users(sf_connection, ids_to_validate)

def connect_to_salesforce(config):
    """Connects to Salesforce and returns the connection object."""
    try:
        sf_client = SalesforceClient(config)
        return sf_client.connect()
    except (ValueError, configparser.NoSectionError, FileNotFoundError) as e:
        print(f"Configuration or Connection Error: {e}")
        return None

def main():
    """Main function to parse arguments and dispatch commands."""
    parser = argparse.ArgumentParser(description="A modular Salesforce admin tool.")
    subparsers = parser.add_subparsers(dest='command', required=True, help='Available commands')

    # --- Pre-flight Command ---
    parser_preflight = subparsers.add_parser('preflight', help='Run a pre-flight duplicate check.')
    parser_preflight.add_argument('--input', type=str, required=True, help="Path to the source Excel (.xlsx) file.")
    parser_preflight.add_argument('--output', type=str, default='preflight_report.csv', help="Path to save the pre-flight CSV report.")
    parser_preflight.set_defaults(func=handle_preflight)

    # --- Create-Users Command ---
    parser_create = subparsers.add_parser('create-users', help='Create users from a pre-flight report.')
    parser_create.add_argument('--input', type=str, required=True, help="Path to the pre-flight CSV report.")
    parser_create.add_argument('--excel-source', type=str, required=True, help="Path to the original Excel file for persona mapping.")
    parser_create.add_argument('--output', type=str, default='creation_results.csv', help="Path to save the creation results CSV.")
    parser_create.add_argument('--no-dry-run', action='store_false', dest='dry_run', help="Disable dry-run mode to make live changes.")
    parser_create.set_defaults(dry_run=True, func=handle_create_users)

    # --- Validate Command ---
    parser_validate = subparsers.add_parser('validate', help='Validate created users in Salesforce.')
    parser_validate.add_argument('--input', type=str, required=True, help="Path to the creation results CSV.")
    parser_validate.add_argument('--excel-source', type=str, required=True, help="Path to the original Excel file to check the 'added by' column.")
    parser_validate.set_defaults(func=handle_validate)

    args = parser.parse_args()

    config = configparser.ConfigParser()
    if not os.path.exists('config.ini'):
        print("Error: 'config.ini' not found. Please create it from 'config.ini.example'.")
        return
    config.read('config.ini')

    args.func(args, config)

if __name__ == '__main__':
    main()
