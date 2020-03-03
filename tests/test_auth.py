import unittest
import configparser
from uipath_api import auth
import os
import datetime

ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class TestAuth(unittest.TestCase):

    def setUp(self) -> None:
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(ROOT, r'files\creds.ini'))

    def test_cloud_auth(self):
        """
        First iteration assumes there's a uipath_api/files/creds.ini file with the below section and keys.
        Tests the Cloud.authenticate method.
        """
        cloud = auth.Cloud(
            orchestrator='',
            user_key=self.config.get('CLOUD', 'user_key'),
            client_id=self.config.get('CLOUD', 'client_id'),
            tenant_logical_name=self.config.get('CLOUD', 'tenant_logical_name'),
            account_logical_name=self.config.get('CLOUD', 'account_logical_name'),
        )
        response = cloud.authenticate()  # Authenticates the session
        self.assertEqual(response.status_code, 200)

    def test_cloud_seconds_until_auth_expires(self):
        """
        Tests whether the function returns an int (success) or a None (fail).
        """
        cloud = auth.Cloud(
            orchestrator='',
            user_key=self.config.get('CLOUD', 'user_key'),
            client_id=self.config.get('CLOUD', 'client_id'),
            tenant_logical_name=self.config.get('CLOUD', 'tenant_logical_name'),
            account_logical_name=self.config.get('CLOUD', 'account_logical_name'),
        )
        cloud.authenticate()
        seconds = cloud.seconds_until_auth_expires()
        self.assertIsInstance(seconds, float)

    def test_cloud_datetime_auth_expires_on(self):
        """
        Tests whether the function returns a datetime object (success), or None (fail).
        """
        cloud = auth.Cloud(
            orchestrator='',
            user_key=self.config.get('CLOUD', 'user_key'),
            client_id=self.config.get('CLOUD', 'client_id'),
            tenant_logical_name=self.config.get('CLOUD', 'tenant_logical_name'),
            account_logical_name=self.config.get('CLOUD', 'account_logical_name'),
        )
        cloud.authenticate()
        expires_on = cloud.datetime_auth_expires_on()
        self.assertIsInstance(expires_on, datetime.datetime)