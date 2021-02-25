from django import forms
from . import models

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit



def get_ebay_settings_form(user, post=None):
    if post:
        return EbaySettingsProfileForm(
            post, instance=models.EbaySettingsProfile.objects.get(user=user))
    return EbaySettingsProfileForm(instance=models.EbaySettingsProfile.objects.get(
        user=user))


def get_sell_settings_form(user, post=None):
    if post:
        return SellSettingsProfileForm(
            post, instance=models.SellSettingsProfile.objects.get(user=user))
    return SellSettingsProfileForm(instance=models.SellSettingsProfile.objects.get(
        user=user))


class EbaySettingsProfileForm(forms.ModelForm):
    class Meta:
        model = models.EbaySettingsProfile
        exclude = ['user']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['country_code'].help_text = 'Cannot make any guarantees for ' \
                                                'trading outside of US.'

        self.helper = FormHelper()
        self.helper.form_id = 'id-settingsForm'
        self.helper.form_class = 'settingsForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'ebay_settings'
        self.helper.add_input(Submit('submit', 'Submit'))


class SellSettingsProfileForm(forms.ModelForm):
    class Meta:
        model = models.SellSettingsProfile
        exclude = ['user']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['shipping_cost'].label = 'Shipping Cost ($)'
        self.fields['shipping_cost'].help_text = 'Shipping is included in price for ' \
                                                 'starting bid, after the percentage ' \
                                                 'off (see below) has been applied.'

        self.fields['percentage_off_average'].label = 'Percentage Off Average Price'
        self.fields['percentage_off_average'].help_text = 'Example: A card price ' \
                                                          'average for a particular ' \
                                                          'card is $4.00. By setting ' \
                                                          'this to 0.25, the starting ' \
                                                          'bid for the card would be ' \
                                                          'set at $3.00 (25% off).'

        self.helper = FormHelper()
        self.helper.form_id = 'id-settingsForm'
        self.helper.form_class = 'settingsForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'sell_settings'
        self.helper.help_text_inline = True
        self.helper.add_input(Submit('submit', 'Submit'))
