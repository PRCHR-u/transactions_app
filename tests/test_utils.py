import json
from datetime import datetime
from unittest.mock import patch

import pandas as pd
import pytest

from src.utils import (
    get_card_summaries,
    get_currency_rates,
    get_date_range,
    get_greeting,
    get_stock_prices,
    get_top_transactions,
)


@pytest.mark.parametrize(
    "hour,expected", [
        (6, "Доброе утро"),
        (12, "Добрый день"),
        (18, "Добрый вечер"),
        (23, "Доброй ночи")
        ]
)
def test_get_greeting(hour, expected):
    result = json.loads(get_greeting(hour))
    assert result["greeting"] == expected


def test_get_date_range():
    input_date = "2023-10-15 14:30:00"
    result = json.loads(get_date_range(input_date))
    assert result["start_date"] == "2023-10-01 00:00:00"
    assert result["end_date"] == "2023-10-15 14:30:00"


@pytest.mark.parametrize(
    "transactions_data,expected",
    [
        (
            [
                {
                    "Дата операции": "2023-10-01",
                    "Номер карты": "1234567890123456",
                    "Сумма операции": -1262.00,
                    "Кешбэк": 12.62,
                    "Категория": "Супермаркеты",
                    "Описание": "Лента",
                },
                {
                    "Дата операции": "2023-10-15",
                    "Номер карты": "6543210987654321",
                    "Сумма операции": -1198.23,
                    "Кешбэк": 11.98,
                    "Категория": "Переводы",
                    "Описание": "Перевод",
                },
            ],
            [
                {
                    "last_digits": "3456",
                    "total_spent": 1262.00,
                    "cashback": 12.62
                    },
                {
                    "last_digits": "4321",
                    "total_spent": 1198.23,
                    "cashback": 11.98
                    },
            ],
        ),
        (
            [
                {
                    "Дата операции": "2023-10-01",
                    "Номер карты": "1234567890123456",
                    "Сумма операции": -100.00,
                    "Кешбэк": 1.00,
                    "Категория": "Супермаркеты",
                    "Описание": "Магазин",
                }
            ],
            [{"last_digits": "3456", "total_spent": 100.00, "cashback": 1.00}],
        ),
    ],
)
def test_get_card_summaries(transactions_data, expected):
    df = pd.DataFrame(transactions_data)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"])
    start_date = datetime(2023, 10, 1)
    end_date = datetime(2023, 10, 31)
    result = json.loads(get_card_summaries(df, start_date, end_date))
    assert result == expected


@pytest.mark.parametrize(
    "transactions_data,expected",
    [
        (
            [
                {
                    "Дата операции": "2023-10-01",
                    "Сумма операции": -1262.00,
                    "Категория": "Супермаркеты",
                    "Описание": "Лента",
                },
                {
                    "Дата операции": "2023-10-15",
                    "Сумма операции": -1198.23,
                    "Категория": "Переводы",
                    "Описание": "Перевод",
                },
            ],
            [
                {
                    "date": "01.10.2023",
                    "amount": 1262.00,
                    "category": "Супермаркеты",
                    "description": "Лента"
                },
                {
                    "date": "15.10.2023",
                    "amount": 1198.23,
                    "category": "Переводы",
                    "description": "Перевод"
                },
            ],
        ),
        (
            [
                {
                    "Дата операции": "2023-10-01",
                    "Сумма операции": -100.00,
                    "Категория": "Супермаркеты",
                    "Описание": "Магазин",
                }
            ],
            [
                {
                    "date": "01.10.2023",
                    "amount": 100.00,
                    "category": "Супермаркеты",
                    "description": "Магазин"
                }
            ],
        ),
    ],
)
def test_get_top_transactions(transactions_data, expected):
    df = pd.DataFrame(transactions_data)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"])
    start_date = datetime(2023, 10, 1)
    end_date = datetime(2023, 10, 31)
    result = json.loads(get_top_transactions(df, start_date, end_date))
    assert result == expected


@patch("src.utils.get_currency_rates")
def test_get_currency_rates(mock_get_rates):
    mock_get_rates.return_value = [
        {"currency": "USD", "rate": 0.0136},
        {"currency": "EUR", "rate": 0.0115}
        ]
    result = json.loads(get_currency_rates())
    assert result == [
        {"currency": "USD", "rate": 0.0136},
        {"currency": "EUR", "rate": 0.0115}
    ]


@patch("src.utils.get_stock_prices")
def test_get_stock_prices(mock_get_prices):
    mock_get_prices.return_value = [
        {"stock": "AAPL", "price": 150.12},
        {"stock": "AMZN", "price": 3173.18},
        {"stock": "GOOGL", "price": 2742.39},
        {"stock": "MSFT", "price": 296.71},
        {"stock": "TSLA", "price": 1007.08},
    ]
    result = json.loads(get_stock_prices())
    assert result == [
        {"stock": "AAPL", "price": 150.12},
        {"stock": "AMZN", "price": 3173.18},
        {"stock": "GOOGL", "price": 2742.39},
        {"stock": "MSFT", "price": 296.71},
        {"stock": "TSLA", "price": 1007.08},
    ]
