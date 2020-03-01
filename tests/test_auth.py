import unittest
import configparser
from uipath_api import auth
import os

ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class TestAuth(unittest.TestCase):

	def setUp(self) -> None:
		self.config = configparser.ConfigParser()
		self.config.read(os.path.join(ROOT, r'files\creds.ini'))

	def test_cloud_auth(self):
		"""
		Tests the Cloud.authenticate and Cloud.test_auth() methods.
		First iteration, this might change in the future.
		:return:
		"""
		cloud = auth.Cloud(
			user_key=self.config.get('CLOUD', 'user_key'),
			client_id=self.config.get('CLOUD', 'client_id'),
			tenant_logical_name=self.config.get('CLOUD', 'tenant_logical_name'),
			account_logical_name=self.config.get('CLOUD', 'account_logical_name'),
		)

		cloud.authenticate()  # Authenticates the session
		response = cloud.test_auth()  # Tests if the session is authenticated by requesting the Orch license.
		assert response.status_code == 200
