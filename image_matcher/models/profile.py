import decimal

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class WebUserManager(models.Manager):
    pass


class WebUser(get_user_model()):
    objects = WebUserManager()

    class Meta:
        proxy = True

    @property
    def access_token(self):
        return self.user_tokens_profile.access_token

    @access_token.setter
    def access_token(self, value):
        self.user_tokens_profile.access_token = value
        self.user_tokens_profile.save()

    @property
    def refresh_token(self):
        return self.user_tokens_profile.refresh_token

    @refresh_token.setter
    def refresh_token(self, value):
        self.user_tokens_profile.refresh_token = value
        self.user_tokens_profile.save()

    @staticmethod
    def get_user(user):
        return WebUser.objects.get(username=user.username)


class UserTokensProfile(models.Model):
    user = models.OneToOneField(get_user_model(), related_name='user_tokens_profile',
                                on_delete=models.PROTECT)
    access_token = models.CharField(max_length=2500, null=True, blank=True)
    refresh_token = models.CharField(max_length=150, null=True, blank=True)


class EbaySettingsProfile(models.Model):
    user = models.OneToOneField(get_user_model(), related_name='ebay_settings_profile',
                                on_delete=models.PROTECT)
    paypal_email = models.EmailField(blank=True, null=True)
    country_code = models.CharField(max_length=10, default='US', null=True, blank=True)
    postal_code = models.CharField(max_length=12, null=True, blank=True)


class SellSettingsProfile(models.Model):
    user = models.OneToOneField(get_user_model(), related_name='sell_settings_profile',
                                on_delete=models.PROTECT)
    shipping_cost = models.DecimalField(max_digits=4, decimal_places=2,
                                        default=decimal.Decimal(2.50))
    percentage_off_average = models.DecimalField(max_digits=4, decimal_places=4,
                                                 default=decimal.Decimal(0.10))
    fixed_price_item = models.BooleanField(default=True, blank=True)
    best_offer_enabled = models.BooleanField(default=True, blank=True)


@receiver(post_save, sender=get_user_model())
def create_user_tokens_profile(sender, instance, created, **kwargs):
    if created:
        UserTokensProfile.objects.create(user=instance)
        EbaySettingsProfile.objects.create(user=instance)
        SellSettingsProfile.objects.create(user=instance)


@receiver(post_save, sender=get_user_model())
def save_user_tokens_profile(sender, instance, created, **kwargs):
    instance.user_tokens_profile.save()
    instance.ebay_settings_profile.save()
    instance.sell_settings_profile.save()
