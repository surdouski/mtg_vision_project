# -*- coding: utf-8 -*-
"""
Copyright 2019 eBay Inc.
 
Licensed under the Apache License, Version 2.0 (the "License");
You may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,

WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

See the License for the specific language governing permissions and
limitations under the License.
"""
import os
import json
import urllib
import requests
import logging
from . import model
from .model import util
from datetime import datetime, timedelta
from .credentialutil import credentialutil
from .model.model import oAuth_token, credentials
from image_matcher.models import AppCredential

LOGFILE = 'eBay_Oauth_log.txt'
logging.basicConfig(level=logging.DEBUG, filename=LOGFILE, format="%(asctime)s: %(levelname)s - %(funcName)s: %(message)s", filemode='w')


app_scopes = [
    "https://api.ebay.com/oauth/api_scope",
    "https://api.ebay.com/oauth/api_scope/sell.inventory",
    "https://api.ebay.com/oauth/api_scope/sell.marketing",
    "https://api.ebay.com/oauth/api_scope/sell.account",
    "https://api.ebay.com/oauth/api_scope/sell.fulfillment"
]


def get_instance_oauth2api(app_config_path):
    credentialutil.load(app_config_path)
    oauth2api_inst = oauth2api()
    return oauth2api_inst


class oauth2api(object):

    @staticmethod
    def generate_user_authorization_url(scopes, state=None):
        credential = AppCredential.objects.get_app_credential()
        scopes = ' '.join(scopes)
        param = {
            'client_id': credential.app_id,
            'redirect_uri': credential.redirect_uri,
            'response_type': 'code',
            'prompt': 'login',
            'scope': scopes,
        }
        
        if state is not None:
            param.update({'state': state})
        query = urllib.parse.urlencode(param)
        return f'{credential.web_endpoint}?{query}'

    def get_application_token(self, env_type, scopes):
        """
            makes call for application token and stores result in credential object
            returns credential object
        """
      
        logging.info("Trying to get a new application access token ... ")        
        credential = AppCredential.objects.get_app_credential()
        headers = util._generate_request_headers(credential)
        body = util._generate_application_request_body(credential, ' '.join(scopes))
        
        resp = requests.post(credential.api_endpoint, data=body, headers=headers)
        print(body)
        content = json.loads(resp.content)
        token = oAuth_token()     
    
        if resp.status_code == requests.codes.ok:
            token.access_token = content['access_token']
            # set token expiration time 5 minutes before actual expire time
            token.token_expiry = datetime.utcnow()+timedelta(seconds=int(content['expires_in']))-timedelta(minutes=5)

        else:
            token.error = str(resp.status_code) + ': ' + content['error_description']
            logging.error("Unable to retrieve token.  Status code: %s - %s", resp.status_code, requests.status_codes._codes[resp.status_code])
            logging.error("Error: %s - %s", content['error'], content['error_description'])
        return token     
    

    def exchange_code_for_access_token(self, env_type, code):       
        logging.info("Trying to get a new user access token ... ")  
        credential = AppCredential.objects.get_app_credential()
    
        headers = util._generate_request_headers(credential)
        body = util._generate_oauth_request_body(credential, code)
        print(f'headers: {headers}')
        print(f'body: {body}')

        resp = requests.post(credential.api_endpoint, data=body, headers=headers)
            
        content = json.loads(resp.content)
        token = oAuth_token()     
        
        if resp.status_code == requests.codes.ok:
            token.access_token = content['access_token']
            token.token_expiry = datetime.utcnow()+timedelta(seconds=int(content['expires_in']))-timedelta(minutes=5)
            token.refresh_token = content['refresh_token']
            token.refresh_token_expiry = datetime.utcnow()+timedelta(seconds=int(content['refresh_token_expires_in']))-timedelta(minutes=5)
        else:
            token.error = str(resp.status_code) + ': ' + content['error_description']
            logging.error("Unable to retrieve token.  Status code: %s - %s", resp.status_code, requests.status_codes._codes[resp.status_code])
            logging.error("Error: %s - %s", content['error'], content['error_description'])
        return token
    
    
    def get_access_token(self, env_type, refresh_token, scopes):
        """
        refresh token call
        """
        
        logging.info("Trying to get a new user access token ... ")

        credential = AppCredential.objects.get_app_credential()
    
        headers = util._generate_request_headers(credential)
        body = util._generate_refresh_request_body(' '.join(scopes), refresh_token)
        resp = requests.post(credential.api_endpoint, data=body, headers=headers)
        content = json.loads(resp.content)
        token = oAuth_token()        
        token.token_response = content    
    
        if resp.status_code == requests.codes.ok:
            token.access_token = content['access_token']
            token.token_expiry = datetime.utcnow()+timedelta(seconds=int(content['expires_in']))-timedelta(minutes=5)
        else:
            token.error = str(resp.status_code) + ': ' + content['error_description']
            logging.error("Unable to retrieve token.  Status code: %s - %s", resp.status_code, requests.status_codes._codes[resp.status_code])
            logging.error("Error: %s - %s", content['error'], content['error_description'])
        return token


class RefreshAccessTokenCredentials:
    def __init__(self, app_id, cert_id, dev_id, redirect_uri, api_endpoint,
                 refresh_token):
        self.client_id = app_id
        self.client_secret = cert_id
        self.dev_id = dev_id
        self.ru_name = redirect_uri
        self.api_endpoint = api_endpoint
        self.refresh_token = refresh_token


def get_access_token(refresh_token):
    logging.info("Trying to get a new user access token ... ")

    """
    credential = credentials(refresh_access_token_credentials.app_id,
                             refresh_access_token_credentials.dev_id,
                             refresh_access_token_credentials.cert_id,
                             refresh_access_token_credentials.redirect_uri)
    """
    credential = AppCredential.objects.get_app_credential()
    headers = util._generate_request_headers(credential)
    body = util._generate_refresh_request_body(' '.join(app_scopes), refresh_token)
    resp = requests.post(credential.api_endpoint, data=body, headers=headers)
    content = json.loads(resp.content)
    token = oAuth_token()
    token.token_response = content['access_token']

    if resp.status_code == requests.codes.ok:
        token.access_token = content['access_token']
        token.token_expiry = datetime.utcnow() + timedelta(
            seconds=int(content['expires_in'])) - timedelta(minutes=5)
    else:
        token.error = str(resp.status_code) + ': ' + content['error_description']
        logging.error("Unable to retrieve token.  Status code: %s - %s",
                      resp.status_code,
                      requests.status_codes._codes[resp.status_code])
        logging.error("Error: %s - %s", content['error'],
                      content['error_description'])
    return token, credential
