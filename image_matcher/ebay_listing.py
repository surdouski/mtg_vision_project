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
        token, credential = AppCredential.objects.get_app_credential(
            domain=self.domain).get_access_token(web_user.refresh_token)
        web_user.access_token = token.access_token
        web_user.save()
        return Trading(compatability=719, appid=credential.app_id,
                       certid=credential.cert_id, devid=credential.dev_id,
                       token=token.access_token, config=None, domain=self.domain)

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

        item_payload = self.item_payload(listing_title, listed_price, ebay_image_url)
        try:
            response = self.api.execute('AddItem', item_payload)
            response.raise_for_status()
        except HTTPError as e:
            print(logging.exception(str(e)))
            raise

    def item_payload(self, listing_title, listed_price, ebay_image_url):
        ebay_settings = self.user.ebay_settings_profile
        print(ebay_image_url)
        return {
            "Item": {
                "Title": listing_title,
                "Description": f"Each auction is for 1 copy of shown card.  The card you will receive is displayed in"
                               f" the image.",
                "PrimaryCategory": {
                    "CategoryID": "183454"
                },
                "StartPrice": f"{listed_price}",
                "CategoryMappingAllowed": "true",
                "Country": f"{ebay_settings.country_code}",
                "ConditionID": "3000",
                "Currency": "USD",
                "DispatchTimeMax": "3",
                "ListingDuration": "Days_7",
                "ListingType": "Chinese",
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
                    "ReturnsWithinOption": "Days_30",
                    "ShippingCostPaidByOption": "Buyer"
                },
                "ShippingDetails": {
                    "ShippingType": "Flat",
                    "ShippingServiceOptions": {
                        "ShippingServicePriority": "1",
                        "ShippingService": "USPSMedia",
                        "ShippingServiceCost": "2.50"
                    }
                },
                "Site": f"{ebay_settings.country_code}",
                "Location": f"{ebay_settings.country_code}"
            }
        }
    """
    @property
    def api(self):
        return self._api

    @property
    def price(self):
        print(self._price)
        if self._price and self._percent_off and self._shipping:
            print('inside')
            return two_digits((self._price * (Decimal(1.00) - self._percent_off)) - self._shipping)"""

    '''@property
    def label(self):
        return f"Name: {self.card_name}, Set: {self.card_set}, Price: ${self.price}"'''

    """def set_price(self, new_price=None):
        if new_price:
            self._price = new_price
        else:
            self._price = fetch_card_price(self.card_id, self._is_foil)"""

    """def adjust_five_percent_up(self):
        self._percent_off -= Decimal(0.05)

    def adjust_five_percent_down(self):
        self._percent_off += Decimal(0.05)"""

    '''def activate_api(self):
        """Required for ebay -> app id, dev id, cert id, and token in ebay.yaml:
        For more detailed information on these items, please visit
        'ebaysdk' on github.
        """

        self._api = Trading(config_file=f"{PROJECT_ROOT}/ebay.yaml", domain=self._domain)
        return self._api'''

    '''def upload_image(self):
        """Uploads to ebay server for use in listing."""

        files = {'file': ('EbayImage', open(self.image_path, 'rb'))}
        picture_data = {
            "WarningLevel": "Low",
            "PictureName": self.title,
        }
        response = self.api.execute('UploadSiteHostedPictures', picture_data, files=files)
        self._image_url = response.reply.get('SiteHostedPictureDetails').get('FullURL')
        return self._image_url'''

    '''def create_listing(self):
        """Requires image to be uploaded."""

        try:
            if self.image_url:
                response = self.api.execute('AddItem', self.item_payload)
                return response.reply
            raise Exception('Must upload image before creating listing.')
        except ConnectionError as e:
            print(e)
            print(e.response.dict())'''

    '''def perform_create(self):
        self.activate_api()
        self.upload_image()
        self.create_listing()'''


'''def two_digits(number):
    return Decimal(number).quantize(Decimal('0.01'))'''








'''def __init__(self, image_path, card, is_foil=False, shipping=Decimal(2.50),
             percent_off=Decimal(0.10), domain='api.sandbox.ebay.com'):
    self.image_path = image_path
    self.card_id = card['id']
    self.card_name = card['name']
    self.card_set = card['set']

    self._is_foil = is_foil
    """self._domain = domain
    self._shipping = two_digits(shipping)
    self._percent_off = two_digits(percent_off)

    self._price = self.set_price()
    self._api = None
    self._image_url = None"""
'''