import unittest
from unittest.mock import MagicMock
import pandas as pd
from src.org_analyzer import (
    get_users_by_permission_set,
    list_permissions_by_modified_date,
    list_connected_apps,
    get_connected_app_details
)

class TestOrgAnalyzer(unittest.TestCase):

    def setUp(self):
        """Set up a mock Salesforce connection."""
        self.mock_sf = MagicMock()

    def test_get_users_by_permission_set(self):
        """Test the get_users_by_permission_set function."""
        self.mock_sf.query_all.return_value = {'records': [{'Assignee.Name': 'Test User'}]}
        df = get_users_by_permission_set(self.mock_sf, 'TestPermSet')
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty)
        self.mock_sf.query_all.assert_called_once()

    def test_list_permissions_by_modified_date(self):
        """Test the list_permissions_by_modified_date function."""
        self.mock_sf.query_all.return_value = {'records': [{'Name': 'TestPermSet'}]}
        df = list_permissions_by_modified_date(self.mock_sf)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty)
        self.mock_sf.query_all.assert_called_once()

    def test_list_connected_apps(self):
        """Test the list_connected_apps function."""
        self.mock_sf.query_all.return_value = {'records': [{'Name': 'TestApp'}]}
        df = list_connected_apps(self.mock_sf)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty)
        self.mock_sf.query_all.assert_called_once()

    def test_get_connected_app_details_found(self):
        """Test get_connected_app_details when an app is found."""
        self.mock_sf.query.return_value = {'totalSize': 1, 'records': [{'Name': 'TestApp'}]}
        df = get_connected_app_details(self.mock_sf, 'TestApp')
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty)
        self.mock_sf.query.assert_called_once()

    def test_get_connected_app_details_not_found(self):
        """Test get_connected_app_details when an app is not found."""
        self.mock_sf.query.return_value = {'totalSize': 0, 'records': []}
        df = get_connected_app_details(self.mock_sf, 'NonExistentApp')
        self.assertIsNone(df)
        self.mock_sf.query.assert_called_once()

if __name__ == '__main__':
    unittest.main()
