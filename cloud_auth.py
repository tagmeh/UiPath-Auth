import base64
import hashlib
import json
import re
import os

import requests


def generate_challenege(code_verifier):
    code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode('utf-8')
    code_challenge = code_challenge.replace('=', '')
    code_challenge, len(code_challenge)
    return code_challenge


def generate_verifier():
    code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode('utf-8')
    code_verifier = re.sub('[^a-zA-Z0-9]+', '', code_verifier)
    code_verifier, len(code_verifier)
    return code_verifier


def uipath_auth(request):
    verifier = generate_verifier()
    challenge = generate_challenege(verifier)
    url = f'https://account.uipath.com/authorize?response_type=code&nonce=b0f368cbc59c6b99ccc8e9b66a30b4a6&state=47441df4d0f0a89da08d43b6dfdc4be2&code_challenge={challenge}&code_challenge_method=S256&scope=openid+profile+offline_access+email &audience=https%3A%2F%2Forchestrator.cloud.uipath.com&client_id=5v7PmPJL6FOGu6RB8I1Y4adLBhIwovQN&redirect_uri=https%3A%2F%2Faccount.uipath.com%2Fmobile'
    data = {
        'success': True,
        'url': url,
        'verifier': verifier,
        'challenge': challenge,
    }


def get_token_data(url_code, verifier_code):
    url = 'https://account.uipath.com/oauth/token'
    get_refresh_token_data = {
        "grant_type": "authorization_code",
        "code": url_code,
        "redirect_uri": "https://account.uipath.com/mobile",
        "code_verifier": verifier_code,
        "client_id": "5v7PmPJL6FOGu6RB8I1Y4adLBhIwovQN"
    }
    # Get access_token, id_token, and refresh_token
    response = requests.post(url, data=get_refresh_token_data)
    print('get_token_data', response)
    response_json = json.loads(response.text)
    return response_json


def get_accounts_for_user(id_token):
    url = 'https://platform.uipath.com/cloudrpa/api/getAccountsForUser'
    header = {'Authorization': f'Bearer {id_token}'}
    response = requests.get(url, headers=header)
    print('get_accounts_for_user', response)
    response_json = json.loads(response.text)
    return response_json


def get_service_instance_logical_name(account_logical_name, id_token):
    url = f'https://platform.uipath.com/cloudrpa/api/account/{account_logical_name}/getAllServiceInstances'
    header = {'Authorization': f'Bearer {id_token}'}
    response = requests.get(url, headers=header)
    print('get_service_instance_logical_name', response)
    response_json = json.loads(response.text)
    return response_json


def get_auth_data(url_code, challenge, verifier):
    auth_dict = {}
    response_json = get_token_data(url_code, verifier)
    auth_dict['access_token'] = response_json['access_token']
    auth_dict['refresh_token'] = response_json['refresh_token']
    auth_dict['id_token'] = response_json['id_token']
    response_json = get_accounts_for_user(auth_dict['id_token'])
    auth_dict['user_email'] = response_json['userEmail']
    auth_dict['account_name'] = response_json['accounts'][0]['accountName']
    auth_dict['account_logical_name'] = response_json['accounts'][0]['accountLogicalName']
    response_json = get_service_instance_logical_name(auth_dict['account_logical_name'], auth_dict['id_token'])
    auth_dict['service_instance_name'] = response_json[0]['serviceInstanceName']
    auth_dict['service_instance_logical_name'] = response_json[0]['serviceInstanceLogicalName']
    auth_dict['service_url'] = response_json[0]['serviceUrl']
    auth_dict['header'] = {
        'Authorization': f'Bearer {auth_dict["access_token"]}',
        'X-UIPATH-TenantName': auth_dict['service_instance_logical_name']
    }
    return auth_dict


def uipath_auth_url(request):
    url = request.GET.get('url', None)
    verifier = request.GET.get('verifier', None)
    challenge = request.GET.get('challenge', None)
    try:
        url_code = url.split('code=')[1].split('&state')[0]
    except IndexError:
        pass
    auth_dict = get_auth_data(url_code, challenge, verifier)
    data = {
        'success': True,
        'refresh_token': auth_dict['refresh_token'],
        'user_email': auth_dict['user_email'],
        'account_name': auth_dict['account_name'],
        'account_logical_name': auth_dict['account_logical_name'],
        'service_instance_name': auth_dict['service_instance_name'],
        'service_instance_logical_name': auth_dict['service_instance_logical_name'],
        'service_url': auth_dict['service_url'],
        'access_token': auth_dict['access_token'],
        'id_token': auth_dict['id_token'],
    }
