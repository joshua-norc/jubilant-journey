import pandas as pd

def load_mapping(filepath):
    """
    Loads a .properties file into a dictionary.
    Handles keys with escaped spaces.
    """
    mapping = {}
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Split only on the first equals sign
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        key = parts[0].replace('\\', '').strip()
                        value = parts[1].strip()
                        mapping[key] = value
    except FileNotFoundError:
        print(f"Error: Mapping file not found at {filepath}")
        return None
    return mapping

def map_row_to_payload(row, mapping):
    """
    Maps a row of data (pandas Series) to a Salesforce payload dictionary.
    """
    payload = {}
    for source_col, sf_field in mapping.items():
        if source_col in row and pd.notna(row[source_col]):
            payload[sf_field] = row[source_col]
    return payload

if __name__ == '__main__':
    # Example Usage
    # Create a dummy mapping file for testing
    with open('dummy_mapping.properties', 'w') as f:
        f.write("Source\ Column\ 1 = Field_1__c\n")
        f.write("Source Column 2 = Field_2__c\n")

    mapping = load_mapping('dummy_mapping.properties')
    print("Loaded Mapping:")
    print(mapping)

    # Create a dummy data row
    data_row = pd.Series({'Source Column 1': 'Value1', 'Source Column 2': 'Value2'})

    payload = map_row_to_payload(data_row, mapping)
    print("\nGenerated Payload:")
    print(payload)

    # Clean up dummy file
    import os
    os.remove('dummy_mapping.properties')
