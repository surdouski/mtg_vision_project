from decimal import Decimal

import requests
from requests import HTTPError


def fetch_card_price(card_id, foil=False):
    try:
        response = requests.get(f'https://api.scryfall.com/cards/{card_id}')
        if not foil:
            if response.json().get('prices').get('usd') is None:
                return None
            return Decimal(response.json().get('prices').get('usd')).quantize(Decimal('0.01'))
        if foil:
            if response.json().get('prices').get('usd_foil') is None:
                return None
            return Decimal(response.json().get('prices').get('usd_foil')).quantize(Decimal('0.01'))
    except HTTPError as http_err:
        return
