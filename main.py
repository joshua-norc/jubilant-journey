import argparse
import configparser
import os
import pandas as pd
from src.salesforce_client import SalesforceClient
from src.data_processor import process_dataframes
from src.user_creator import create_salesforce_users
from src.reporter import generate_report
import src.org_analyzer as analyzer

def handle_provision(args, config):
    """Handles the user provisioning process."""
    # ... (this function remains the same)
    try:
        settings = config['settings']
        environment = settings.get('environment', 'Training')
    except KeyError:
        print("Error: [settings] section not found or incomplete in config.ini.")
        return

    print(f"--- Starting User Provisioning ---")
    print(f"Environment: {environment}")
    print(f"Input Path: {args.input}")
    print(f"Dry Run Mode: {args.dry_run}")

    try:
        if os.path.isdir(args.input):
            user_df = pd.read_csv(os.path.join(args.input, 'training_template.csv'))
            persona_df = pd.read_csv(os.path.join(args.input, 'persona_mapping.csv'))
            sso_df = pd.read_csv(os.path.join(args.input, 'tsso_trainthetrainer.csv'))
        elif os.path.isfile(args.input) and args.input.endswith('.xlsx'):
            excel_file = pd.ExcelFile(args.input)
            user_df = excel_file.read('training template')
            persona_df = excel_file.read('persona mapping')
            sso_df = excel_file.read('TSSO_TrainTheTrainer')
        else:
            print(f"Error: Input path '{args.input}' is not a valid directory or .xlsx file.")
            return
    except Exception as e:
        print(f"An error occurred while loading data: {e}")
        return

    processed_data = process_dataframes(user_df, persona_df, sso_df, environment)
    if processed_data is None or processed_data.empty:
        print("No user data to process.")
        return

    sf_connection = None
    if not args.dry_run:
        sf_connection = connect_to_salesforce(config)
        if not sf_connection: return

    created_user_ids = create_salesforce_users(sf_connection, processed_data, args.dry_run)
    if not args.dry_run and sf_connection and created_user_ids:
        print("\n--- Generating Post-run Report ---")
        generate_report(sf_connection, created_user_ids)

    print("\n--- User Provisioning Finished ---")


def handle_report(args, config):
    """Handles the org reporting process."""
    print("--- Starting Org Reporting ---")
    sf_connection = connect_to_salesforce(config)
    if not sf_connection: return

    result_df = None
    if args.report_type == 'users-by-permset':
        if not args.name:
            print("Error: --name is required for the users-by-permset report.")
            return
        result_df = analyzer.get_users_by_permission_set(sf_connection, args.name)
    elif args.report_type == 'list-permissions':
        result_df = analyzer.list_permissions_by_modified_date(sf_connection)
    elif args.report_type == 'list-connected-apps':
        result_df = analyzer.list_connected_apps(sf_connection)
    elif args.report_type == 'app-details':
        if not args.name:
            print("Error: --name is required for the app-details report.")
            return
        result_df = analyzer.get_connected_app_details(sf_connection, args.name)

    if result_df is not None and not result_df.empty:
        print("\n--- Report Results ---")
        print(result_df.to_string())
        if args.output:
            try:
                result_df.to_csv(args.output, index=False)
                print(f"\nReport saved to {args.output}")
            except Exception as e:
                print(f"\nError saving report to file: {e}")
    else:
        print("No results to display.")

    print("\n--- Org Reporting Finished ---")


def connect_to_salesforce(config):
    # ... (this function remains the same)
    try:
        print("Connecting to Salesforce...")
        sf_client = SalesforceClient(config)
        sf_connection = sf_client.connect()
        if not sf_connection:
            print("Halting due to Salesforce connection failure.")
            return None
        return sf_connection
    except (ValueError, configparser.NoSectionError, FileNotFoundError) as e:
        print(f"Configuration or Connection Error: {e}")
        return None

def main():
    """Main function to parse arguments and dispatch commands."""
    parser = argparse.ArgumentParser(description="A Salesforce admin tool for user provisioning and reporting.")
    subparsers = parser.add_subparsers(dest='command', required=True, help='Available commands')

    # --- Provision Command ---
    parser_provision = subparsers.add_parser('provision', help='Provision users based on an input file.')
    parser_provision.add_argument('--input', type=str, default='data', help="Path to input data (directory of CSVs or a single .xlsx file).")
    parser_provision.add_argument('--no-dry-run', action='store_false', dest='dry_run', help="Disable dry-run mode to make live changes.")
    parser_provision.set_defaults(dry_run=True, func=handle_provision)

    # --- Report Command ---
    parser_report = subparsers.add_parser('report', help='Generate reports about the Salesforce org.')
    parser_report.add_argument('--output', type=str, help="Path to save the report as a CSV file.")
    report_subparsers = parser_report.add_subparsers(dest='report_type', required=True, help="Type of report to generate")

    # Report: users-by-permset
    parser_users_by_permset = report_subparsers.add_parser('users-by-permset', help='List users assigned to a specific permission set.')
    parser_users_by_permset.add_argument('--name', type=str, help='The name of the permission set.')

    # Report: list-permissions
    report_subparsers.add_parser('list-permissions', help='List all permission sets, sorted by last modified date.')

    # Report: list-connected-apps
    report_subparsers.add_parser('list-connected-apps', help='List all connected apps.')

    # Report: app-details
    parser_app_details = report_subparsers.add_parser('app-details', help='Get details for a specific connected app.')
    parser_app_details.add_argument('--name', type=str, help='The name of the connected app.')

    parser_report.set_defaults(func=handle_report)

    args = parser.parse_args()

    # Read configuration
    config = configparser.ConfigParser()
    if not os.path.exists('config.ini'):
        if args.command == 'provision' and args.dry_run:
            print("Warning: 'config.ini' not found. Proceeding with dry run using default settings.")
            config['settings'] = {'environment': 'Training'}
        else:
            print("Error: 'config.ini' not found. Please create it from 'config.ini.example' for live runs or reports.")
            return
    else:
        config.read('config.ini')

    args.func(args, config)

if __name__ == '__main__':
    main()
