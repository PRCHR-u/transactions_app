import os
from unittest.mock import MagicMock, patch

import requests
from dotenv import load_dotenv

load_dotenv()

EXCHANGE_RATES_API_KEY = os.getenv('EXCHANGE_RATES_API_KEY')
EXCHANGE_RATES_URL = "https://api.apilayer.com/currency_data/live"

def get_currency_rates() -> dict:
    """
    Получает актуальные курсы валют относительно RUB.
    Возвращает словарь с курсами валют.
    """
    try:
        headers = {
            "apikey": EXCHANGE_RATES_API_KEY
        }
        params = {
            "base": "RUB",
            "symbols": "USD,EUR,GBP,CNY,JPY"
        }
        response = requests.get(EXCHANGE_RATES_URL, headers=headers, params=params)
        response.raise_for_status()
        rates = response.json().get("rates", {})
        return rates
    except (requests.RequestException, KeyError):
        return {} 