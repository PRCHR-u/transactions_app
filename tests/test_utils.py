from datetime import datetime

import pandas as pd
import pytest

from src.utils import (
    get_card_summaries,
    get_currency_rates,
    get_date_range,
    get_greeting,
    get_stock_prices,
    get_top_transactions,
    read_transactions,
)


@pytest.mark.parametrize("hour, expected_greeting", [
    (6, "Доброе утро"),
    (12, "Добрый день"),
    (18, "Добрый вечер"),
    (23, "Доброй ночи")
])
def test_get_greeting(hour, expected_greeting):
    assert get_greeting(hour) == expected_greeting

def test_get_date_range(sample_transactions):
    start, end = get_date_range("2023-10-15 14:30:00")
    assert start == datetime(2023, 10, 1, 0, 0)
    assert end == datetime(2023, 10, 15, 14, 30)

def test_get_card_summaries(sample_transactions):
    start, end = get_date_range("2023-10-15 14:30:00")
    summaries = get_card_summaries(sample_transactions, start, end)
    assert summaries == [
        {"last_digits": "3456", "total_spent": 1269.94, "cashback": 12.70},
        {"last_digits": "4321", "total_spent": 1198.23, "cashback": 11.98}
    ]

def test_get_top_transactions(sample_transactions):
    start, end = get_date_range("2023-10-15 14:30:00")
    top_transactions = get_top_transactions(sample_transactions, start, end)
    assert top_transactions == [
        {"date": "01.10.2023", "amount": 1262.00, "category": "Супермаркеты", "description": "Лента"},
        {"date": "15.10.2023", "amount": 1198.23, "category": "Переводы", "description": "Перевод Кредитная карта. ТП 10.2 RUR"},
        {"date": "10.10.2023", "amount": 7.94, "category": "Супермаркеты", "description": "Магнит"}
    ]

def test_get_currency_rates(mock_currency_rates_response):
    rates = get_currency_rates(["USD", "EUR"])
    assert rates == [
        {"currency": "USD", "rate": 0.0136},
        {"currency": "EUR", "rate": 0.0115}
    ]

def test_get_stock_prices(mock_stock_prices_response):
    prices = get_stock_prices(["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"])
    assert prices == [
        {"stock": "AAPL", "price": 150.12},
        {"stock": "AMZN", "price": 3173.18},
        {"stock": "GOOGL", "price": 2742.39},
        {"stock": "MSFT", "price": 296.71},
        {"stock": "TSLA", "price": 1007.08}
    ]
