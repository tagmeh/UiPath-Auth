import requests
from requests import exceptions as request_exceptions
import json
import time
import datetime


class Session:
    access_token = None
    _last_refresh = None
    _expires_in = None
    scope = None

    def ok(self):
        try:
            if self.seconds_until_auth_expires() <= 0:
                return False
            else:
                return True
        except TypeError:
            raise TypeError('Session is not authenticated.')

    def seconds_until_auth_expires(self):
        if self._last_refresh is None:
            print('No initial authentication time.')
            return None
        elif self._last_refresh < 0:
            print('API access expired {0} seconds ago.'.format(self._last_refresh - self._expires_in))
            return None
        else:
            elapsed = time.time() - self._last_refresh
            return self._expires_in - elapsed

    def datetime_auth_expires_on(self):
        seconds = self.seconds_until_auth_expires()
        if seconds:
            return datetime.datetime.now() + datetime.timedelta(seconds=seconds)
        else:
            return None


class Local(Session):
    """
    Authenticates with the local UiPath Orchestrator
    Returns an api token.
    """
    def __init__(self,
                 orchestrator: str,
                 tenant: str,
                 username: str,
                 password: str
                 ):
        self.orchestrator = orchestrator
        self.tenant = tenant
        self.username = username
        self.password = password

    @property
    def url(self):
        """"""
        if self.orchestrator is None:
            raise TypeError(
                'Missing Orchestrator string. (Currently "{0}") Update the "orchestrator" attribute.'.format(
                    type(self.orchestrator)))
        else:
            return "{0}/api/Account/Authenticate".format(self.orchestrator)

    @property
    def bearer_token(self):
        """ The access_token changes on each authentication. Lasts 24 hours as of 2/2020 (formerly 1 hour) """
        if self.access_token:
            return 'Bearer {0}'.format(self.access_token)
        else:
            return None

    @property
    def header(self):
        """  """
        return {
            'Authorization': self.bearer_token,
        }

    @property
    def data(self):
        """"""
        return {
            "tenancyName": self.tenant,
            "usernameOrEmailAddress": self.username,
            "password": self.password,
        }

    def authenticate(self):
        try:
            response = requests.post(self.url, json=self.data, verify=False)
        except request_exceptions.ConnectionError:
            return None

        if not response.ok:
            print('Authentication failed with ', response, response.reason)

        content = json.loads(response.text)

        self.access_token = content['result']
        self._last_refresh = time.time()
        self._expires_in = content['expires_in']
        self.scope = content['scope']

        return response

    def test_auth(self):
        """
        Tests the current authentication session by attempting to pull the orchestrator license.
        :return:
        """
        # Might be a different URL for the local orchestrator.
        license_url = r'{}/odata/Settings/UiPath.Server.Configuration.OData.GetLicense'.format(self.orchestrator)
        response = requests.get(license_url, headers=self.header)
        return response


class Cloud(Session):
    def __init__(self,
                 orchestrator: str,
                 user_key: str,
                 client_id: str,
                 tenant_logical_name: str,
                 account_logical_name: str,
                 ):
        self.orchestrator = orchestrator
        self.user_key = user_key
        self.client_id = client_id
        self.tenant_logical_name = tenant_logical_name
        self.account_logical_name = account_logical_name

        self.auth_url = r'https://account.uipath.com/oauth/token'

        self.id_token = None

    @property
    def url(self):
        """ """
        if self.orchestrator is None:
            raise TypeError(
                'Missing Orchestrator string. (Currently "{0}") Update the "orchestrator" attribute.'.format(
                    type(self.orchestrator)))
        else:
            return '{0}/{1}/{2}'.format(self.orchestrator, self.account_logical_name, self.tenant_logical_name)

    @property
    def bearer_token(self):
        """ The access_token changes on each authentication. Lasts 24 hours as of 2/2020 (formerly 1 hour) """
        return 'Bearer {0}'.format(self.access_token)

    @property
    def header(self):
        """  """
        return {
            'Authorization': self.bearer_token,
            'X-UIPATH-TenantName': self.tenant_logical_name
        }

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

        return response

    def test_auth(self):
        license_url = r'https://platform.uipath.com/odata/Settings/UiPath.Server.Configuration.OData.GetLicense'
        response = requests.get(license_url, headers=self.header)
        return response
