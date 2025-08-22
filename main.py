import argparse
from src.salesforce_client import SalesforceClient
from src.data_processor import load_and_process_data
from src.user_creator import create_salesforce_users

def main():
    """
    Main function to run the Salesforce user provisioning process.
    """
    parser = argparse.ArgumentParser(description="Salesforce User Provisioning Tool")
    parser.add_argument(
        '--environment',
        type=str,
        default='Training',
        choices=['QA2', 'Training', 'Prod'],
        help="The target Salesforce environment."
    )
    # The default is now to do a dry run, unless --no-dry-run is specified
    parser.add_argument(
        '--no-dry-run',
        action='store_false',
        dest='dry_run',
        help="Disable dry-run mode. If this flag is present, the script will make changes in Salesforce."
    )
    parser.set_defaults(dry_run=True)

    parser.add_argument(
        '--data-dir',
        type=str,
        default='data',
        help="The directory where the CSV files are located."
    )
    args = parser.parse_args()

    print(f"--- Starting Salesforce User Provisioning ---")
    print(f"Environment: {args.environment}")
    print(f"Dry Run Mode: {args.dry_run}")

    # Load and process data
    training_file = f'{args.data_dir}/training_template.csv'
    persona_file = f'{args.data_dir}/persona_mapping.csv'
    sso_file = f'{args.data_dir}/tsso_trainthetrainer.csv'

    try:
        processed_data = load_and_process_data(training_file, persona_file, sso_file, args.environment)
    except ValueError as e:
        print(f"Error during data processing: {e}")
        return

    if processed_data is None:
        print("Halting due to errors in data loading.")
        return

    if processed_data.empty:
        print("No user data to process.")
        return

    # Connect to Salesforce if not a dry run
    sf_connection = None
    if not args.dry_run:
        try:
            print("Connecting to Salesforce...")
            sf_client = SalesforceClient()
            sf_connection = sf_client.connect()
            if not sf_connection:
                print("Halting due to Salesforce connection failure.")
                return
        except ValueError as e:
            print(f"Error: {e}")
            print("Please set the required Salesforce environment variables (SF_USERNAME, SF_PASSWORD, SF_SECURITY_TOKEN, SF_INSTANCE_URL).")
            return

    # Create users
    create_salesforce_users(sf_connection, processed_data, args.dry_run)

    print("--- Salesforce User Provisioning Finished ---")

if __name__ == '__main__':
    main()
