import requests
from requests import exceptions as request_exceptions


# todo: Fix this function to allow different orchestrators.
# todo: maybe expect a string like "prod" or "dev" for the branch, then do the utils function inside this one.
def uipath_local_auth(orch_url):
    """
    Authenticates with the local UiPath Orchestrator
    Returns an api token.
    """

    tenant = ''
    username = ''
    password = ''

    data = {
        "tenancyName": tenant,
        "usernameOrEmailAddress": username,
        "password": password,
    }
    # Local orchestrator
    url = f"{orch_url}/api/Account/Authenticate"

    # Authentication POST request
    try:
        response = requests.post(url, json=data, verify=False)
    except request_exceptions.ConnectionError:
        return None

    return response.json()["result"]
