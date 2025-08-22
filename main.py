import argparse
import configparser
import os
import pandas as pd
from src.salesforce_client import SalesforceClient
from src.data_processor import process_dataframes
from src.user_creator import create_salesforce_users
from src.reporter import generate_report

def main():
    """
    Main function to run the Salesforce user provisioning process.
    """
    parser = argparse.ArgumentParser(description="Salesforce User Provisioning Tool")
    parser.add_argument(
        '--input',
        type=str,
        default='data',
        help="Path to the input data. Can be a directory of CSV files or a single Excel (.xlsx) file."
    )
    parser.add_argument(
        '--no-dry-run',
        action='store_false',
        dest='dry_run',
        help="Disable dry-run mode. If this flag is present, the script will make changes in Salesforce."
    )
    parser.set_defaults(dry_run=True)
    args = parser.parse_args()

    # Read configuration
    config = configparser.ConfigParser()
    if not os.path.exists('config.ini'):
        print("Error: 'config.ini' not found. Please create it by copying 'config.ini.example' and filling in your details.")
        return
    config.read('config.ini')

    try:
        settings = config['settings']
        environment = settings.get('environment', 'Training')
    except KeyError:
        print("Error: [settings] section not found in config.ini.")
        return

    print(f"--- Starting Salesforce User Provisioning ---")
    print(f"Environment: {environment}")
    print(f"Input Path: {args.input}")
    print(f"Dry Run Mode: {args.dry_run}")

    # Load data
    try:
        if os.path.isdir(args.input):
            print("Input is a directory, loading CSV files...")
            user_df = pd.read_csv(os.path.join(args.input, 'training_template.csv'))
            persona_df = pd.read_csv(os.path.join(args.input, 'persona_mapping.csv'))
            sso_df = pd.read_csv(os.path.join(args.input, 'tsso_trainthetrainer.csv'))
        elif os.path.isfile(args.input) and args.input.endswith('.xlsx'):
            print("Input is an Excel file, loading sheets...")
            excel_file = pd.ExcelFile(args.input)
            user_df = excel_file.read('training template')
            persona_df = excel_file.read('persona mapping')
            sso_df = excel_file.read('TSSO_TrainTheTrainer')
        else:
            print(f"Error: Input path '{args.input}' is not a valid directory or .xlsx file.")
            return
    except FileNotFoundError as e:
        print(f"Error loading data file: {e}")
        return
    except Exception as e:
        print(f"An error occurred while loading data: {e}")
        return

    # Process data
    try:
        processed_data = process_dataframes(user_df, persona_df, sso_df, environment)
    except ValueError as e:
        print(f"Error during data processing: {e}")
        return

    if processed_data is None or processed_data.empty:
        print("No user data to process.")
        return

    # Connect to Salesforce if not a dry run
    sf_connection = None
    if not args.dry_run:
        try:
            print("Connecting to Salesforce...")
            sf_client = SalesforceClient(config)
            sf_connection = sf_client.connect()
            if not sf_connection:
                print("Halting due to Salesforce connection failure.")
                return
        except (ValueError, configparser.NoSectionError, FileNotFoundError) as e:
            print(f"Configuration or Connection Error: {e}")
            print("Please ensure your config.ini is correctly set up and any specified files (like a private key) exist.")
            return

    # Create users and get the list of created IDs
    created_user_ids = create_salesforce_users(sf_connection, processed_data, args.dry_run)

    # Generate report for live runs
    if not args.dry_run and sf_connection and created_user_ids:
        print("\n--- Generating Post-run Report ---")
        generate_report(sf_connection, created_user_ids)

    print("\n--- Salesforce User Provisioning Finished ---")

if __name__ == '__main__':
    main()
