import environ

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

    def __str__(self):
        return f'{self.domain}'
