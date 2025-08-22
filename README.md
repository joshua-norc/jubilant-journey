# Salesforce User Provisioning Tool

This project provides a Python-based command-line tool to automate the provisioning of users in Salesforce. It reads user data from CSV files, processes it according to a persona-based mapping, and creates the corresponding user records in a target Salesforce organization, including assigning permissions and configuring Single Sign-On (SSO).

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

*   Python 3.6+
*   pip (Python package installer)

### Installation

1.  Clone the repository to your local machine:
    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2.  Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

Before running the application, you need to set up your configuration file.

1.  Make a copy of the example configuration file:
    ```bash
    cp config.ini.example config.ini
    ```

2.  Open `config.ini` in a text editor and fill in your Salesforce credentials. The tool supports two authentication methods:

    *   **Username/Password:** Fill in `username`, `password`, and `security_token`.
    *   **Connected App (JWT):** Fill in `username`, `consumer_key`, and the path to your `private_key_file`.

    You also need to configure the settings under the `[settings]` section, such as the `environment` (e.g., `Training`, `Prod`) you are targeting.

    **Note:** The `config.ini` file is included in `.gitignore` to prevent accidental commits of your credentials.

## Usage

To run the application, use the `main.py` script from the root of the project directory.

### Dry Run (Default)

By default, the application runs in **dry-run mode**. This will simulate the entire process, printing out the actions that would be taken (like user creation and permission assignments) without making any actual changes in your Salesforce org. This is useful for verifying your data and configuration.

```bash
python3 main.py
```

### Live Run

To disable dry-run mode and make live changes in Salesforce, use the `--no-dry-run` flag.

**Warning:** This will create and modify records in your Salesforce organization. Use with caution.

```bash
python3 main.py --no-dry-run
```

The script will output its progress to the console. If any errors occur, they will be printed to the console. Upon successful completion of a live run, a CSV report of the created users will be generated in the `reports/` directory.

## Project Structure

```
.
├── config.ini.example      # Example configuration file.
├── data/                   # Directory for input CSV files.
│   ├── persona_mapping.csv
│   ├── training_template.csv
│   └── tsso_trainthetrainer.csv
├── main.py                 # Main entry point of the application.
├── README.md               # This file.
├── reports/                # Directory for output reports (will be created on first run).
├── requirements.txt        # Python package dependencies.
├── src/                    # Source code directory.
│   ├── data_processor.py
│   ├── salesforce_client.py
│   └── user_creator.py
└── tests/                  # Directory for unit tests.
    └── test_data_processor.py
```
