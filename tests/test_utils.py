from unittest.mock import patch

import pytest
import pandas as pd
from datetime import datetime
from src.utils import (
    read_transactions,
    get_date_range,
    get_greeting,
    get_card_summaries,
    get_top_transactions,
    get_currency_rates,
    get_stock_prices
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
        {"last_digits": "3456", "total_spent": 3210.00, "cashback": 36.53},
        {"last_digits": "4321", "total_spent": 1651.23, "cashback": 16.51}
    ]

def test_get_top_transactions(sample_transactions):
    start, end = get_date_range("2023-10-15 14:30:00")
    top_transactions = get_top_transactions(sample_transactions, start, end)
    assert top_transactions == [
        {"date": "15.10.2023", "amount": 14216.42, "category": "Пополнение_BANK007", "description": "Пополнение счета"},
        {"date": "15.10.2023", "amount": 33000.00, "category": "Пополнение_BANK007", "description": "Пополнение счета"},
        {"date": "20.10.2023", "amount": 1198.23, "category": "Переводы", "description": "Перевод Кредитная карта. ТП 10.2 RUR"},
        {"date": "10.10.2023", "amount": 7.94, "category": "Супермаркеты", "description": "Магнит"},
        {"date": "25.10.2023", "amount": 421.00, "category": "Различные товары", "description": "Ozon.ru"}
    ]

def test_get_currency_rates(monkeypatch):
    def mock_get_currency_rates(currencies):
        return [{"currency": "USD", "rate": 84.7458}, {"currency": "EUR", "rate": 91.7431}]

    monkeypatch.setattr("src.utils.get_currency_rates", mock_get_currency_rates)

    result = get_currency_rates(["USD", "EUR"])
    assert result == [{"currency": "USD", "rate": 84.7458}, {"currency": "EUR", "rate": 91.7431}]


# Мокируем get_stock_prices при импорте
@patch("src.utils.get_stock_prices")
def test_get_stock_prices(mock_get_stock_prices):
    mock_get_stock_prices.return_value = [{"stock": "AAPL", "price": 150.12}, {"stock": "TSLA", "price": 1007.08}]
    result = get_stock_prices(["AAPL", "TSLA"])
    assert result == [{"stock": "AAPL", "price": 150.12}, {"stock": "TSLA", "price": 1007.08}]
