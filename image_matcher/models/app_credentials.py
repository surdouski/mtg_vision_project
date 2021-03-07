import base64
import logging
import urllib
import environ
import requests

from datetime import datetime, timedelta

from django.db import models


env = environ.Env(DOMAIN=str)
environ.Env.read_env()


class AppCredentialManager(models.Manager):
    def get_app_credential(self, domain=None):
        return self.get(domain=domain) if domain else self.get(domain=env('DOMAIN'))

    def get_user_authorization_url(self):
        """Used to get URL for user to sign in and retrieve oauth tokens on eBay."""

        credential = self.get_app_credential()
        return credential.generate_user_authorization_url()

    def get_oauth_tokens(self, code):
        """Exchange ebay code from uri redirect for oauth tokens.

        Parameters
        ----------
        code: str

        Returns
        -------
        OAuthToken
        """

        logging.info("Trying to get new access and refresh tokens... ")

        credential = self.get_app_credential()
        headers = credential.generate_request_headers()
        body = credential.generate_oauth_tokens_request_body(code)

        response = requests.post(credential.api_endpoint, headers=headers, data=body)
        token = OAuthToken(response)
        return token

    def get_refresh_access_token(self, refresh_token):
        """Exchange refresh token for refreshed access token.

        Parameters
        ----------
        refresh_token: str

        Returns
        -------
        OAuthToken
        """

        logging.info("Trying to get new access token... ")

        credential = self.get_app_credential()
        headers = credential.generate_request_headers()
        body = credential.generate_refresh_access_token_request_body(refresh_token)

        response = requests.post(credential.api_endpoint, headers=headers, data=body)
        token = OAuthToken(response)
        return token


class AppCredential(models.Model):
    domain = models.CharField(max_length=40)
    app_id = models.CharField(max_length=60)  # client_id
    cert_id = models.CharField(max_length=60)  # client_secret
    dev_id = models.CharField(max_length=60)
    redirect_uri = models.CharField(max_length=80)  # ru_name
    web_endpoint = models.CharField(max_length=80)
    api_endpoint = models.CharField(max_length=80)

    objects = AppCredentialManager()
    api = AppCredentialManager()

    @property
    def client_id(self):
        return self.app_id

    @property
    def client_secret(self):
        return self.cert_id

    @property
    def ru_name(self):
        return self.redirect_uri

    def generate_user_authorization_url(self):
        """Used to get URL for user to sign in and retrieve oauth tokens on eBay."""

        param = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'prompt': 'login',
            'scope': ' '.join(_get_app_scopes())
        }
        query = urllib.parse.urlencode(param)
        return self.web_endpoint + '?' + query

    def generate_request_headers(self):
        """Used for making any POST or GET to eBay API."""

        _credential = self.client_id + ':' + self.client_secret
        b64_encoded_credential = base64.b64encode(_credential.encode('utf-8'))
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic %s' % str(b64_encoded_credential, 'utf-8')
        }
        return headers

    def generate_oauth_tokens_request_body(self, code):
        """Used to make body for oauth tokens (access/refresh) from ebay API."""

        body = {
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri,
            'code': code
        }
        return body

    @staticmethod
    def generate_refresh_access_token_request_body(refresh_token):
        """Used to make body to get new access token from refresh token."""

        body = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'scope': ' '.join(_get_app_scopes())
        }
        return body

    def __str__(self):
        return f'{self.domain}'


class OAuthToken:
    @property
    def access_token(self):
        return self._access_token

    @property
    def token_expiry(self):
        return self._token_expiry

    @property
    def refresh_token(self):
        return self._refresh_token

    @property
    def refresh_token_expiry(self):
        return self._refresh_token_expiry

    @property
    def error(self):
        return self._error

    def __init__(self, response):
        self._access_token = None
        self._token_expiry = None
        self._refresh_token = None
        self._refresh_token_expiry = None
        self._error = None

        content = response.json()
        if response.status_code == requests.codes.ok:
            self.set_access_token(content)
            self.set_refresh_token(content)
        else:
            self.log_error(content, response)

    def set_access_token(self, content):
        if content.get('access_token'):
            self._access_token = content.get('access_token')
            _expires_in = int(content.get('expires_in'))
            self._token_expiry = datetime.utcnow() + timedelta(seconds=_expires_in)

    def set_refresh_token(self, content):
        if content.get('refresh_token'):
            self._refresh_token = content.get('refresh_token')
            _expires_in = int(content.get('refresh_token_expires_in'))
            self._refresh_token_expiry = datetime.utcnow() + timedelta(seconds=_expires_in)

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
        if self.refresh_token is not None:
            token_str += '"refresh_token": "' + self.refresh_token + '", "expires_in": ' \
                                                                     '"' \
                         + self.refresh_token_expiry.strftime('%Y-%m-%dT%H:%M:%S:%f') \
                         + '"'
        token_str += '}'
        return token_str


def _get_app_scopes():
    return [
        "https://api.ebay.com/oauth/api_scope",
        "https://api.ebay.com/oauth/api_scope/sell.inventory",
        "https://api.ebay.com/oauth/api_scope/sell.marketing",
        "https://api.ebay.com/oauth/api_scope/sell.account",
        "https://api.ebay.com/oauth/api_scope/sell.fulfillment"
    ]
