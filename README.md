# Salesforce Admin Tool

This project provides a Python-based command-line tool to automate common Salesforce administrative tasks, including user provisioning and org analysis.

## Getting Started

(Instructions for Installation and Configuration remain the same)

## Usage

The application uses a command-line interface with two main commands: `provision` and `report`.

### Command: `provision`

This command runs a comprehensive user provisioning workflow. It now exclusively uses an Excel file as input, and writes the results back to new sheets in that same file.

#### Workflow Steps:
1.  **Pre-flight Duplicate Check**: Before any action is taken, the script reads the `Users2Add` sheet from your input Excel file and queries Salesforce for potential duplicates based on Email and Username.
2.  **Pre-flight Report**: The results of the check are written to a new sheet in your workbook called `preflight`. This sheet shows which users will be created and which will be skipped.
3.  **User Creation**: The script proceeds to create the users who are not identified as duplicates.
4.  **Result Tracking**: The final status of each user creation (Success, Failed, Skipped, or Success with errors) is updated in the `preflight` sheet.
5.  **`UsersCreated` Sheet**: A new sheet named `UsersCreated` is added to your workbook, containing the Salesforce ID and applied configurations for all successfully created users.
6.  **Final Validation**: A summary of the created users is printed to the console for immediate visual confirmation.

#### Arguments:
*   `--input <path>`: **(Required)** Path to the input Excel (`.xlsx`) file. This file must contain sheets named `Users2Add`, `Persona Mapping`, and `TSSO_TrainTheTrainer`.
*   `--no-dry-run`: Disables dry-run mode to make live changes in Salesforce. **Warning:** Use with caution.

#### Example:

*   **Perform a live run using an Excel file:**
    ```bash
    python3 main.py provision --input /path/to/my_users.xlsx --no-dry-run
    ```

### Command: `report`

This command generates various ad-hoc reports about the Salesforce org.

(Report command documentation remains the same)
