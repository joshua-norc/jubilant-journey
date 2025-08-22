import pandas as pd
import os

# More realistic data based on user feedback
users_data = {
    'Email (employee ID version)': ['001@norc.org', '002@norc.org', '003@norc.org'],
    'Email (name version)': ['Brunt-Kelli@norc.org', 'Cooper-Tina@norc.org', 'Gaines-Littel@norc.org'],
    'FirstName': ['Kelli', 'Tina', 'Littel'],
    'LastName': ['Brunt', 'Cooper', 'Gaines'],
    'Persona Name': ['Tier 1 Supervisor', 'Tier 1 Rep - English', 'Tier 1 Rep - Spanish/Bilingual'],
    'Username': ['Brunt-Kelli@norc.org@test.com', 'Cooper-Tina@norc.org@test.com', 'Gaines-Littel@norc.org@test.com'],
    'Alias': ['kbrunt', 'tcooper', 'lgaines'],
    'TimeZoneSidKey': ['America/Chicago', 'America/New_York', 'America/Los_Angeles'],
    'LocaleSidKey': ['en_US', 'en_US', 'en_US'],
    'LanguageLocaleKey': ['en_US', 'en_US', 'es_MX'],
    'EmailEncodingKey': ['UTF-8', 'UTF-8', 'UTF-8'],
    'IsActive': [True, True, False],
    'UserPermissionsInteractionUser': [True, False, True],
    'Is_Migrated__c': [False, False, False],
    'Contact Center': ['center1', 'center2', 'center3'],
    'FederationIdentifier': ['kbrunt', 'tcooper', 'lgaines'],
    'added by': ['Josh', 'Not Josh', 'Josh'] # For validation testing
}
users_df = pd.DataFrame(users_data)

persona_data = {
    'Persona Name': ['Tier 1 Supervisor', 'Tier 1 Rep - English', 'Tier 1 Rep - Spanish/Bilingual'],
    'Profile ID (Training)': ['prof1', 'prof2', 'prof2'],
    'Role ID (Training)': ['role1', 'role2', 'role3'],
    'Permission Set Group IDs (Training)': ['psg1', 'psg2', 'psg2;psg3'],
    'Contact Center Training': ['cc1', 'cc2', 'cc3'],
    'Queues': ['Queue1', 'Queue2\nQueue3', 'Queue4']
}
persona_df = pd.DataFrame(persona_data)

tsso_data = {
    'Email (employee ID version)': ['001@norc.org', '003@norc.org'],
    'Email (name version)': ['Brunt-Kelli@norc.org', 'Gaines-Littel@norc.org'],
    'First Name': ['Kelli', 'Littel'], 'Last Name': ['Brunt', 'Gaines'],
    'Persona Name': ['Tier 1 Supervisor', 'Tier 1 Rep - Spanish/Bilingual']
}
tsso_df = pd.DataFrame(tsso_data)

if not os.path.exists('reports'):
    os.makedirs('reports')

# Write to Excel with the new sheet name
with pd.ExcelWriter('reports/test_users.xlsx') as writer:
    users_df.to_excel(writer, sheet_name='Training Template', index=False)
    persona_df.to_excel(writer, sheet_name='Persona Mapping', index=False)
    tsso_df.to_excel(writer, sheet_name='TSSO_TrainTheTrainer', index=False)

print("Created/updated reports/test_users.xlsx with new data and sheet name.")
