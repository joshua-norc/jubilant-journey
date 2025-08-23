# Salesforce Admin Tool

This project provides a Python-based command-line tool to automate common Salesforce administrative tasks. The main workflow is a multi-step user provisioning process, but it also includes ad-hoc reporting capabilities.

## Getting Started

### Prerequisites
* Python 3.6+
* pip

### Installation
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`

### Configuration
1.  **Create `config.ini`:** Copy `config.ini.example` to `config.ini` and fill in your Salesforce credentials. For sandbox connections, the easiest method is to set `domain = test`. For production or developer orgs, use `instance_url = login.salesforce.com`.
2.  **Create `mapping.properties`:** Create a `mapping.properties` file. This file controls how columns in your spreadsheet map to fields in Salesforce. The format is `Spreadsheet Column Name=SalesforceApiFieldName`.

## User Provisioning Workflow

This workflow allows you to safely check for duplicates, create users, and validate the results in three distinct, file-based steps.

### Step 1: `preflight`
This command runs a duplicate check against your Salesforce org.

*   **Input:** An Excel file (`.xlsx`) containing a sheet named `Training Template`.
*   **Action:** Queries Salesforce for users with matching emails or usernames from the input sheet. The search is based on the `Email (name version)` column.
*   **Output:** A CSV file (`preflight_report.csv` by default) that lists every user from the input and an `Action` column indicating whether they are a potential duplicate or safe to create.

*   **Example:**
    ```bash
    python3 main.py preflight --input path/to/MyUserList.xlsx --output preflight_v1.csv
    ```

### Step 2: `create-users`
This command creates users in Salesforce based on the results of a pre-flight check, using the field mappings you provide.

*   **Input:**
    1. A pre-flight CSV report (the output from Step 1).
    2. The original source Excel file (for persona and SSO mapping).
*   **Action:** Creates users who are marked as `Create New User` in the pre-flight report. It uses your `mapping.properties` file to build the user record.
*   **Output:** A CSV file (`creation_results.csv` by default) with the detailed results of each user creation attempt.

*   **Example (Live Run):**
    ```bash
    python3 main.py create-users --input preflight_v1.csv --excel-source path/to/MyUserList.xlsx --no-dry-run
    ```

### Step 3: `validate`
This command runs a final validation check on the users who were successfully created, with special filtering logic.

*   **Input:**
    1. A creation results CSV file (the output from Step 2).
    2. The original source Excel file.
*   **Action:** Queries Salesforce for the users with a "Success" status. It then filters these users to only those where the `added by` column in the source Excel file is 'Josh'.
*   **Output:** A summary table printed to the console for immediate visual inspection.

*   **Example:**
    ```bash
    python3 main.py validate --input creation_results.csv --excel-source path/to/MyUserList.xlsx
    ```

## Ad-hoc Reporting
The `report` command can be used to generate various ad-hoc reports about the Salesforce org. (See `--help` for more details).
