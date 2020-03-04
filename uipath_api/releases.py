import requests
from requests import exceptions as request_exceptions
import json
import time
import datetime

from .classes.releases_response import ReleasesResponse


class Releases():
    def __init__(self, session):
        self.session = session

    def session_check(self):
        if self.session.ok:
            return True
        else:
            self.session = self.session.authenticate()
            if self.session.ok:
                return True
            else:
                return False

    # def call
