from decimal import Decimal

#from ebaysdk.trading import Connection as Trading
#from ebaysdk.exception import ConnectionError

#from settings import PROJECT_ROOT, PAYPAL_EMAIL, COUNTRY, POSTAL_CODE

#from .fetch_data import fetch_card_price


class CardListingObject:
    def __init__(self, image_path, card, is_foil=False, shipping=Decimal(2.50),
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

    """@property
    def item_payload(self):
        return {
            "Item": {
                "Title": self.title,
                "Description": f"Each auction is for 1 copy of shown card.  The card you will receive is displayed in"
                               f" the image.",
                "PrimaryCategory": {
                    "CategoryID": "183454"
                },
                "StartPrice": f"{self.price}",
                "CategoryMappingAllowed": "true",
                "Country": f"{COUNTRY}",
                "ConditionID": "3000",
                "Currency": "USD",
                "DispatchTimeMax": "3",
                "ListingDuration": "Days_7",
                "ListingType": "Chinese",
                "PaymentMethods": "PayPal",
                "PayPalEmailAddress": f"{PAYPAL_EMAIL}",
                "PictureDetails": {
                    "PictureURL": self._image_url
                },
                "PostalCode": f"{POSTAL_CODE}",
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
                "Site": f"{COUNTRY}"
            }
        }

    @property
    def api(self):
        return self._api"""

    '''@property
    def image_url(self):
        return self._image_url'''

    """@property
    def price(self):
        print(self._price)
        if self._price and self._percent_off and self._shipping:
            print('inside')
            return two_digits((self._price * (Decimal(1.00) - self._percent_off)) - self._shipping)"""

    @property
    def title(self):
        if self._is_foil:
            return f"MTG [*FOIL*] [{self.card_set}]{self.card_name} x 1"
        return f"MTG [{self.card_set}]{self.card_name} x 1"

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
