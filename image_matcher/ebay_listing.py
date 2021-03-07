import logging
import environ
from ebaysdk.trading import Connection as Trading
from requests import HTTPError

from image_matcher.models import AppCredential
from image_matcher.models.profile import WebUser
from mtg_vision_project.settings import MEDIA_ROOT

env = environ.Env(DOMAIN=str)
environ.Env.read_env()


class CardListingObject:
    def __init__(self, listing_details, user):
        self._listing_details = listing_details
        self._user = user
        self._domain = env('DOMAIN')

        self._api = self.activate_api()

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        self._user = value

    @property
    def card_id(self):
        return self._listing_details.scryfall_id

    @property
    def card_name(self):
        return self._listing_details.name

    @property
    def card_set(self):
        return self._listing_details.set

    @property
    def title(self):
        return f"MTG [{self.card_set}]{self.card_name} x 1"

    @property
    def api(self):
        return self._api

    @property
    def domain(self):
        return self._domain

    def activate_api(self):
        """Required for ebay -> app id, dev id, cert id, and token in ebay.yaml:
        For more detailed information on these items, please visit 'ebaysdk' on github.
        Note: Appears to be error code 931 for invalid auth token.
        """

        web_user = WebUser.get_user(self.user)
        credential = AppCredential.api.get_app_credential()
        token = AppCredential.api.get_refresh_access_token(web_user.refresh_token)
        web_user.access_token = token.access_token
        web_user.save()
        return Trading(compatability=719, appid=credential.app_id,
                       certid=credential.cert_id, devid=credential.dev_id,
                       token=token.access_token, config_file=None, domain=self.domain)

    def upload_image(self, image_path):
        """Uploads to ebay server for use in listing."""

        files = {'file': ('EbayImage', open(self._get_abs_path(image_path), 'rb'))}
        picture_data = {
            "WarningLevel": "Low",
            "PictureName": self.title}
        response = self._api.execute('UploadSiteHostedPictures', picture_data,
                                     files=files)
        ebay_image_url = response.reply.get('SiteHostedPictureDetails').get('FullURL')
        return ebay_image_url

    @staticmethod
    def _get_abs_path(image_path):
        return f'{MEDIA_ROOT}/{image_path}'

    def create_listing(self, listing_title, listed_price, ebay_image_url):
        """Requires image to be uploaded."""

        seller_settings_profile = self.user.sell_settings_profile
        listing_type = "FixedPriceItem" if seller_settings_profile.fixed_price_item \
            else "chinese"
        item_payload = self.item_payload(listing_title, listed_price, ebay_image_url,
                                         seller_settings_profile.best_offer_enabled,
                                         seller_settings_profile.shipping_cost,
                                         listing_type)
        try:
            if seller_settings_profile.fixed_price_item:
                api_command = 'AddFixedPriceItem'
            else:
                api_command = 'AddItem'
            response = self.api.execute(api_command, item_payload)
            response.raise_for_status()
        except HTTPError as e:
            print(logging.exception(str(e)))
            raise

    def item_payload(self, listing_title, listed_price, ebay_image_url,
                     best_offer_enabled, shipping_cost, listing_type):
        ebay_settings = self.user.ebay_settings_profile
        print(ebay_image_url)
        return {
            "Item": {
                "Title": listing_title,
                "Description": f"Each auction is for 1 copy of shown card.  The card you will receive is displayed in"
                               f" the image.      "
                               f"\nThis listing was created by mtg-vision.com.",
                "PrimaryCategory": {
                    "CategoryID": "183454"
                },
                "StartPrice": f"{listed_price}",
                "BestOfferDetails": {
                    "BestOfferEnabled": "true" if best_offer_enabled else "false",
                },
                "CategoryMappingAllowed": "true",
                "Country": f"{ebay_settings.country_code}",
                "ConditionID": "3000",
                "Currency": "USD",
                "DispatchTimeMax": "3",
                "ListingDuration": "Days_7",
                "ListingType": f"{listing_type}",
                "PaymentMethods": "PayPal",
                "PayPalEmailAddress": f"{ebay_settings.paypal_email}",
                "PictureDetails": {
                    "PictureURL": ebay_image_url
                },
                "PostalCode": f"{ebay_settings.postal_code}",
                "Quantity": "1",
                "ReturnPolicy": {
                    "ReturnsAcceptedOption": "ReturnsAccepted",
                    "RefundOption": "MoneyBack",
                    "ReturnsWithinOption": "Days_14",
                    "ShippingCostPaidByOption": "Buyer"
                },
                "ShippingDetails": {
                    "ShippingType": "Flat",
                    "ShippingServiceOptions": {
                        "ShippingServicePriority": "1",
                        "ShippingService": "USPSMedia",
                        "ShippingServiceCost": f"{shipping_cost}"
                    }
                },
                "Site": f"{ebay_settings.country_code}",
                "Location": f"{ebay_settings.country_code}"
            }
        }
