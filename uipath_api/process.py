import requests
from requests import exceptions as request_exceptions
import json
import time
import datetime


class Processes:  # Might subclass a model-like class in the future. Similar to BeautifulSoup.
    def __init__(self, session):
        self.session = session

    def valid(self):
        """
        Checks if the current session is valid by checking how long has elapsed since the last authentication call.
        Reauthenticates if necessary, otherwise returns True
        :return: bool
        """
        if self.session.ok:
            return True
        else:
            self.session = self.session.authenticate()
            if self.session.ok:
                return True
            else:
                return False

    def get_all(self):
        """
        Gets a list of Process dictionary objects
        """
        if self.session.valid:
            url = f'{self.session.orchestrator}/odata/Processes'
            response = requests.get(url, headers=self.session.header)
