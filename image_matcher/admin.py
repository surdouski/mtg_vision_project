from django.contrib import admin
from .models import UserTokensProfile, SellSettingsProfile, EbaySettingsProfile

admin.site.register(UserTokensProfile)
admin.site.register(SellSettingsProfile)
admin.site.register(EbaySettingsProfile)
