import requests
from requests import exceptions as request_exceptions
import json
import time
import datetime


class Assets:
    def __init__(self, session):
        self.session = session
