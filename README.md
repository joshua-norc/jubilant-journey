# Salesforce Admin Tool

This project provides a Python-based command-line tool to automate common Salesforce administrative tasks, including user provisioning and org analysis.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Prerequisites

*   Python 3.6+
*   pip (Python package installer)

### Installation

1.  Clone the repository to your local machine.
2.  Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

Before running the application, you must set up your configuration file.

1.  Make a copy of the example configuration file:
    ```bash
    cp config.ini.example config.ini
    ```

2.  Open `config.ini` in a text editor and fill in your Salesforce credentials. The tool supports two authentication methods:
    *   **Username/Password:** Fill in `username`, `password`, and `security_token`.
    *   **Connected App (JWT):** Fill in `username`, `consumer_key`, and the path to your `private_key_file`.

    You also need to configure the target `environment` (e.g., `Training`, `Prod`) under the `[settings]` section.

    **Note:** `config.ini` is gitignored to prevent committing credentials.

## Usage

The application uses a command-line interface with two main commands: `provision` and `report`.

### Command: `provision`

This command provisions users based on an input file.

#### Arguments:
*   `--input <path>`: Path to the input data. Can be a directory of CSV files (defaults to `./data`) or a single Excel (`.xlsx`) file.
*   `--no-dry-run`: Disables dry-run mode to make live changes in Salesforce. **Warning:** Use with caution.

#### Examples:

*   **Perform a dry run using data from the default `./data` directory:**
    ```bash
    python3 main.py provision
    ```

*   **Perform a live run using an Excel file:**
    ```bash
    python3 main.py provision --input /path/to/my_users.xlsx --no-dry-run
    ```

### Command: `report`

This command generates various reports about the Salesforce org.

#### Arguments:
*   `--output <path>`: (Optional) Path to save the report as a CSV file. If omitted, the report is printed to the console.

#### Sub-Commands:

*   **`users-by-permset`**: List users assigned to a specific permission set.
    *   `--name <permset_name>`: The name of the permission set.
    *   Example: `python3 main.py report users-by-permset --name "My_Custom_Permission_Set" --output permset_users.csv`

*   **`list-permissions`**: List all permission sets, sorted by last modified date.
    *   Example: `python3 main.py report list-permissions`

*   **`list-connected-apps`**: List all connected apps.
    *   Example: `python3 main.py report list-connected-apps`

*   **`app-details`**: Get details for a specific connected app.
    *   `--name <app_name>`: The name of the connected app.
    *   Example: `python3 main.py report app-details --name "My_Connected_App"`


## Project Structure

The project is organized into several directories:
*   `src/`: Contains the core Python source code.
*   `data/`: Holds the example input CSV files.
*   `reports/`: The default output directory for generated reports.
*   `tests/`: Contains all unit tests.
