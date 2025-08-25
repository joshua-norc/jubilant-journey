# Salesforce Admin Tool

This project provides a Python-based command-line tool to automate common Salesforce administrative tasks.

## Getting Started
(Instructions for Installation and Configuration remain the same)

## Usage

The application supports two primary modes for user provisioning: a simplified, single-command workflow, and a manual, step-by-step workflow for more granular control.

### Recommended Workflow: `provision`
This single command runs the entire, orchestrated user provisioning workflow. It performs the pre-flight duplicate check, creates new users, and runs a final validation, all in one step. It passes data in memory and produces a single, consolidated CSV report at the end. This is the easiest way to use the tool.

*   **Arguments:**
    *   `--input <path>`: **(Required)** Path to the source Excel (`.xlsx`) file.
    *   `--output <path>`: Path to save the final consolidated CSV report.
    *   `--no-dry-run`: Disables dry-run mode to make live changes.

*   **Example:**
    ```bash
    python3 main.py provision --input path/to/MyUserList.xlsx --output final_report.csv --no-dry-run
    ```

### Manual Step-by-Step Workflow
For advanced users who want to inspect the results of each stage, the following commands can be run in sequence.

#### Step 1: `preflight`
*   **Action:** Runs a duplicate check.
*   **Input:** Source Excel file.
*   **Output:** A `preflight_report.csv` file.
*   **Example:** `python3 main.py preflight --input path/to/MyUserList.xlsx --output preflight.csv`

#### Step 2: `create-users`
*   **Action:** Creates users based on the pre-flight report.
*   **Input:** The `preflight.csv` from Step 1 and the original Excel file.
*   **Output:** A `creation_results.csv` file.
*   **Example:** `python3 main.py create-users --input preflight.csv --excel-source path/to/MyUserList.xlsx`

#### Step 3: `validate`
*   **Action:** Validates the created users.
*   **Input:** The `creation_results.csv` from Step 2 and the original Excel file.
*   **Output:** A summary printed to the console.
*   **Example:** `python3 main.py validate --input creation_results.csv --excel-source path/to/MyUserList.xlsx`

## Ad-hoc Reporting
The `report` command can be used to generate various ad-hoc reports about the Salesforce org. (This functionality is not yet fully implemented).
