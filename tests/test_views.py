import json
from datetime import datetime
from unittest.mock import MagicMock, patch

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
from src.views import events_view, home_view


@pytest.mark.parametrize("transactions_data,expected", [
    (
        [
            {
                "Дата операции": "2023-10-01",
                "Номер карты": "1234567890123456",
                "Сумма операции": -1262.00,
                "Кешбэк": 12.62,
                "Категория": "Супермаркеты",
                "Описание": "Лента"
            },
            {
                "Дата операции": "2023-10-15",
                "Номер карты": "6543210987654321",
                "Сумма операции": -1198.23,
                "Кешбэк": 11.98,
                "Категория": "Переводы",
                "Описание": "Перевод"
            }
        ],
        {
            "greeting": "Добрый день",
            "date_range": {
                "start_date": "2023-10-01 00:00:00",
                "end_date": "2023-10-15 14:30:00"
            },
            "cards": [
                {"last_digits": "3456", "total_spent": 1262.00, "cashback": 12.62},
                {"last_digits": "4321", "total_spent": 1198.23, "cashback": 11.98}
            ],
            "top_transactions": [
                {"date": "01.10.2023", "amount": 1262.00, "category": "Супермаркеты", "description": "Лента"},
                {"date": "15.10.2023", "amount": 1198.23, "category": "Переводы", "description": "Перевод"}
            ],
            "currency_rates": [
                {"currency": "USD", "rate": 0.0136},
                {"currency": "EUR", "rate": 0.0115}
            ],
            "stock_prices": [
                {"stock": "AAPL", "price": 150.12},
                {"stock": "AMZN", "price": 3173.18},
                {"stock": "GOOGL", "price": 2742.39},
                {"stock": "MSFT", "price": 296.71},
                {"stock": "TSLA", "price": 1007.08}
            ]
        }
    ),
    (
        [
            {
                "Дата операции": "2023-10-01",
                "Номер карты": "1234567890123456",
                "Сумма операции": -100.00,
                "Кешбэк": 1.00,
                "Категория": "Супермаркеты",
                "Описание": "Магазин"
            }
        ],
        {
            "greeting": "Добрый день",
            "date_range": {
                "start_date": "2023-10-01 00:00:00",
                "end_date": "2023-10-15 14:30:00"
            },
            "cards": [
                {"last_digits": "3456", "total_spent": 100.00, "cashback": 1.00}
            ],
            "top_transactions": [
                {"date": "01.10.2023", "amount": 100.00, "category": "Супермаркеты", "description": "Магазин"}
            ],
            "currency_rates": [
                {"currency": "USD", "rate": 0.0136},
                {"currency": "EUR", "rate": 0.0115}
            ],
            "stock_prices": [
                {"stock": "AAPL", "price": 150.12},
                {"stock": "AMZN", "price": 3173.18},
                {"stock": "GOOGL", "price": 2742.39},
                {"stock": "MSFT", "price": 296.71},
                {"stock": "TSLA", "price": 1007.08}
            ]
        }
    )
])
def test_home_view(transactions_data, expected, monkeypatch, mock_currency_rates_response, mock_stock_prices_response):
    def mock_read_transactions(file_path):
        return pd.DataFrame(transactions_data)

    monkeypatch.setattr("src.utils.read_transactions", mock_read_transactions)

    # Преобразуем список словарей в JSON-строку
    transactions_json = json.dumps(transactions_data)
    
    response = home_view("2023-10-15 14:30:00", transactions_json)
    assert response == expected

@pytest.mark.parametrize("transactions_data,expected", [
    (
        [
            {
                "Дата операции": "2023-10-01",
                "Номер карты": "1234567890123456",
                "Сумма операции": -1262.00,
                "Кешбэк": 12.62,
                "Категория": "Супермаркеты",
                "Описание": "Лента"
            },
            {
                "Дата операции": "2023-10-15",
                "Номер карты": "6543210987654321",
                "Сумма операции": -1198.23,
                "Кешбэк": 11.98,
                "Категория": "Переводы",
                "Описание": "Перевод"
            }
        ],
        {
            "expenses": {
                "total_amount": 2460.23,
                "main": [
                    {"category": "Супермаркеты", "amount": 1262.00},
                    {"category": "Переводы", "amount": 1198.23},
                    {"category": "Остальное", "amount": 0}
                ],
                "transfers_and_cash": [
                    {"category": "Переводы", "amount": 1198.23},
                    {"category": "Остальное", "amount": 0}
                ]
            },
            "income": {
                "total_amount": 0,
                "main": [
                    {"category": "Остальное", "amount": 0}
                ]
            },
            "currency_rates": [
                {"currency": "USD", "rate": 0.0136},
                {"currency": "EUR", "rate": 0.0115}
            ],
            "stock_prices": [
                {"stock": "AAPL", "price": 150.12},
                {"stock": "AMZN", "price": 3173.18},
                {"stock": "GOOGL", "price": 2742.39},
                {"stock": "MSFT", "price": 296.71},
                {"stock": "TSLA", "price": 1007.08}
            ]
        }
    ),
    (
        [
            {
                "Дата операции": "2023-10-01",
                "Номер карты": "1234567890123456",
                "Сумма операции": -100.00,
                "Кешбэк": 1.00,
                "Категория": "Супермаркеты",
                "Описание": "Магазин"
            }
        ],
        {
            "expenses": {
                "total_amount": 100.00,
                "main": [
                    {"category": "Супермаркеты", "amount": 100.00},
                    {"category": "Остальное", "amount": 0}
                ],
                "transfers_and_cash": [
                    {"category": "Остальное", "amount": 0}
                ]
            },
            "income": {
                "total_amount": 0,
                "main": [
                    {"category": "Остальное", "amount": 0}
                ]
            },
            "currency_rates": [
                {"currency": "USD", "rate": 0.0136},
                {"currency": "EUR", "rate": 0.0115}
            ],
            "stock_prices": [
                {"stock": "AAPL", "price": 150.12},
                {"stock": "AMZN", "price": 3173.18},
                {"stock": "GOOGL", "price": 2742.39},
                {"stock": "MSFT", "price": 296.71},
                {"stock": "TSLA", "price": 1007.08}
            ]
        }
    )
])
def test_events_view(transactions_data, expected, monkeypatch, mock_currency_rates_response, mock_stock_prices_response):
    def mock_read_transactions(file_path):
        return pd.DataFrame(transactions_data)

    monkeypatch.setattr("src.utils.read_transactions", mock_read_transactions)

    # Преобразуем список словарей в JSON-строку
    transactions_json = json.dumps(transactions_data)
    
    response = events_view("2023-10-15 14:30:00", transactions_json)
    assert response == expected
