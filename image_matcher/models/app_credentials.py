import base64
import json
import logging
from datetime import datetime, timedelta

import environ
import requests

from django.db import models


env = environ.Env(DOMAIN=str)
environ.Env.read_env()


class AppCredentialManager(models.Manager):
    def get_app_credential(self, domain=None):
        return self.get(domain=domain) if domain else self.get(domain=env('DOMAIN'))


class AppCredential(models.Model):
    domain = models.CharField(max_length=40)
    app_id = models.CharField(max_length=60)
    cert_id = models.CharField(max_length=60)
    dev_id = models.CharField(max_length=60)
    redirect_uri = models.CharField(max_length=80)
    web_endpoint = models.CharField(max_length=80)
    api_endpoint = models.CharField(max_length=80)

    objects = AppCredentialManager()

    @property
    def client_id(self):
        return self.app_id

    @property
    def client_secret(self):
        return self.cert_id

    @property
    def ru_name(self):
        return self.redirect_uri

    def get_access_token(self, refresh_token):
        """Retrieve access token, given a refresh token.

        Parameters
        ----------
        refresh_token: str

        Returns
        -------
        (OAuthToken, AppCredential)
        """
        try:
            response = requests.post(self.api_endpoint,
                                     data=self._generate_refresh_request_body(refresh_token),
                                     headers=self._generate_request_headers())
            print(response.json())
        except Exception as e:
            logging.exception(str(e))
        return OAuthToken(response), self

    @staticmethod
    def _generate_refresh_request_body(refresh_token):
        body = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'scope': ' '.join(_get_app_scopes())
        }
        return body

    def _generate_request_headers(self):
        _credential = self.client_id + ':' + self.client_secret
        b64_encoded_credential = base64.b64encode(_credential.encode('utf-8'))
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic %s' % str(b64_encoded_credential, 'utf-8')
        }
        return headers

    def __str__(self):
        return f'{self.domain}'


def _get_app_scopes():
    return [
        "https://api.ebay.com/oauth/api_scope",
        "https://api.ebay.com/oauth/api_scope/sell.inventory",
        "https://api.ebay.com/oauth/api_scope/sell.marketing",
        "https://api.ebay.com/oauth/api_scope/sell.account",
        "https://api.ebay.com/oauth/api_scope/sell.fulfillment"
    ]


class OAuthToken:
    @property
    def access_token(self):
        return self._access_token

    @property
    def token_expiry(self):
        return self._token_expiry

    @property
    def error(self):
        return self._error

    def __init__(self, response):
        self._access_token = None
        self._token_expiry = None
        self._error = None
        #content = json.loads(response.content)
        content = response.json()
        if response.status_code == requests.codes.ok:
            self.set_token(content)
        else:
            self.log_error(content, response)

    def set_token(self, content):
        self._access_token = content['access_token']
        _expires_in = int(content['expires_in'])
        self._token_expiry = datetime.utcnow() + timedelta(seconds=_expires_in)

    def log_error(self, content, response):
        self._error = f'{response.status_code}: {content["error_description"]}'
        logging.error(f'Unable to retrieve token. Status code: {response.status_code}')
        logging.error(f'Error: {content["error"]} - {content["error_description"]}')

    def __str__(self):
        token_str = '{'
        if self.error is not None:
            token_str += '"error": "' + self.error + '"'
        elif self.access_token is not None:
            token_str += '"access_token": "' + self.access_token + '", "expires_in": "'\
                         + self.token_expiry.strftime(
                '%Y-%m-%dT%H:%M:%S:%f') + '"'
        token_str += '}'
        return token_str
