import requests
from requests import exceptions as request_exceptions
import json
import time


class Local:
    """
    Authenticates with the local UiPath Orchestrator
    Returns an api token.
    """

    def __init__(self, orchestrator: str, tenant: str, username: str, password: str):
        self.orchestrator = orchestrator
        self.url = f"{self.orchestrator}/api/Account/Authenticate"
        self.tenant = tenant
        self.username = username
        self.password = password
        self.data = {
            "tenancyName": tenant,
            "usernameOrEmailAddress": username,
            "password": password,
        }

    def authenticate(self):
        try:
            response = requests.post(self.url, json=self.data, verify=False)
        except request_exceptions.ConnectionError:
            return None

        return response


class Cloud:
    def __init__(self,
                 user_key,
                 client_id,
                 tenant_logical_name,
                 account_logical_name,
                 ):

        self.orchestrator = None
        self.user_key = user_key
        self.client_id = client_id
        self.tenant_logical_name = tenant_logical_name
        self.account_logical_name = account_logical_name

        self.url = lambda: f'{self.orchestrator}/{self.account_logical_name}/{self.tenant_logical_name}'
        self.auth_url = r'https://account.uipath.com/oauth/token'

        self.id_token = None  #
        self.access_token = None  # Requires "regenerating" the access once per 24 hours (self._expires_in)
        self.bearer_token = lambda: f'Bearer {self.access_token}'  # separated out to allow calling individually
        self.header = lambda: {
            'Authorization': self.bearer_token,
            'X-UIPATH-TenantName': self.tenant_logical_name
        }  # Grabs the latest header information (the bearer token can change).

        self._last_refresh = None  # Time in seconds since the last authentication or regeneration.
        self._expires_in = None  # Duration of authentication a single instance has. Not configurable on the cloud.
        self.scope = None  # The returned authorized activities for the access

    def authenticate(self):
        """ Authenticate with the Cloud Orchestrator """
        header = {
            'Content-Type': 'application/json',
            'X-UIPATH-TenantName': self.tenant_logical_name
        }

        data = {
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'refresh_token': self.user_key  # "User key" was formerly known as the "refresh token"
        }

        response = requests.post(self.auth_url, headers=header, data=json.dumps(data))
        if not response.ok:
            print('Authentication failed with ', response, response.reason)

        content = json.loads(response.text)

        self.id_token = content['id_token']
        self.access_token = content['access_token']
        self._last_refresh = time.time()
        self._expires_in = content['expires_in']
        self.scope = content['scope']

    def regenerate(self):
        data = {
            "grant_type": "refresh_token",
            "client_id": "5v7PmPJL6FOGu6RB8I1Y4adLBhIwovQN",
            "refresh_token": self.user_key
        }

        response = requests.post(self.auth_url, headers=self.header, data=json.dumps(data))

    def time_until_expire(self):
        if self._last_refresh is None:
            print('No initial authentication time.')
        elif self._last_refresh < 0:
            print(f'API access expired {self._last_refresh - self._expires_in} seconds ago.')
        else:
            elapsed = time.time() - self._last_refresh
            return self._expires_in - elapsed
