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
from src.views import events_view, home_view


@pytest.fixture
def sample_transactions():
    data = [
        {
            "Дата операции": "2023-10-01",
            "Номер карты": "1234567890123456",
            "Сумма операции": -1262.00,
            "Кешбэк": 12.62,
            "Категория": "Супермаркеты",
            "Описание": "Лента"
        },
        {
            "Дата операции": "2023-10-10",
            "Номер карты": "1234567890123456",
            "Сумма операции": -7.94,
            "Кешбэк": 0.08,
            "Категория": "Супермаркеты",
            "Описание": "Магнит"
        },
        {
            "Дата операции": "2023-10-15",
            "Номер карты": "6543210987654321",
            "Сумма операции": -1198.23,
            "Кешбэк": 11.98,
            "Категория": "Переводы",
            "Описание": "Перевод Кредитная карта. ТП 10.2 RUR"
        },
        {
            "Дата операции": "2023-10-20",
            "Номер карты": "1234567890123456",
            "Сумма операции": -829.00,
            "Кешбэк": 8.29,
            "Категория": "Супермаркеты",
            "Описание": "Лента"
        },
        {
            "Дата операции": "2023-10-25",
            "Номер карты": "1234567890123456",
            "Сумма операции": -421.00,
            "Кешбэк": 4.21,
            "Категория": "Различные товары",
            "Описание": "Ozon.ru"
        },
        {
            "Дата операции": "2023-09-15",
            "Номер карты": "1234567890123456",
            "Сумма операции": 14216.42,
            "Кешбэк": 0.00,
            "Категория": "Пополнение_BANK007",
            "Описание": "Пополнение счета"
        },
        {
            "Дата операции": "2023-09-20",
            "Номер карты": "6543210987654321",
            "Сумма операции": -453.00,
            "Кешбэк": 4.53,
            "Категория": "Бонусы",
            "Описание": "Кешбэк за обычные покупки"
        },
        {
            "Дата операции": "2023-09-25",
            "Номер карты": "6543210987654321",
            "Сумма операции": 33000.00,
            "Кешбэк": 0.00,
            "Категория": "Пополнение_BANK007",
            "Описание": "Пополнение счета"
        },
        {
            "Дата операции": "2023-08-15",
            "Номер карты": "1234567890123456",
            "Сумма операции": 1242.00,
            "Кешбэк": 12.42,
            "Категория": "Проценты_на_остаток",
            "Описание": "Проценты по остатку"
        },
        {
            "Дата операции": "2023-08-20",
            "Номер карты": "1234567890123456",
            "Сумма операции": 29.00,
            "Кешбэк": 0.29,
            "Категория": "Кэшбэк",
            "Описание": "Кешбэк за обычные покупки"
        },
        {
            "Дата операции": "2023-08-25",
            "Номер карты": "1234567890123456",
            "Сумма операции": 1000.00,
            "Кешбэк": 10.00,
            "Категория": "Переводы",
            "Описание": "Валерий А."
        }
    ]
    df = pd.DataFrame(data)
    df['Дата операции'] = pd.to_datetime(df['Дата операции'])
    return df

def test_home_view(sample_transactions, monkeypatch):
    def mock_read_transactions(file_path):
        return sample_transactions

    monkeypatch.setattr("src.utils.read_transactions", mock_read_transactions)

    response = home_view("2023-10-15 14:30:00")
    assert response["greeting"] == "Добрый день"
    assert response["cards"] == [
        {"last_digits": "3456", "total_spent": 1269.94, "cashback": 12.70},
        {"last_digits": "4321", "total_spent": 1198.23, "cashback": 11.98}
    ]
    assert response["top_transactions"] == [
        {"date": "01.10.2023", "amount": 1262.00, "category": "Супермаркеты", "description": "Лента"},
        {"date": "15.10.2023", "amount": 1198.23, "category": "Переводы", "description": "Перевод Кредитная карта. ТП 10.2 RUR"},
        {"date": "10.10.2023", "amount": 7.94, "category": "Супермаркеты", "description": "Магнит"}
    ]
    assert response["currency_rates"] == [
        {"currency": "USD", "rate": 0.0136},
        {"currency": "EUR", "rate": 0.0115}
    ]
    assert response["stock_prices"] == [
        {"stock": "AAPL", "price": 150.12},
        {"stock": "AMZN", "price": 3173.18},
        {"stock": "GOOGL", "price": 2742.39},
        {"stock": "MSFT", "price": 296.71},
        {"stock": "TSLA", "price": 1007.08}
    ]

def test_events_view(sample_transactions, monkeypatch):
    def mock_read_transactions(file_path):
        return sample_transactions

    monkeypatch.setattr("src.utils.read_transactions", mock_read_transactions)

    response = events_view("2023-10-15 14:30:00")
    assert response["expenses"]["total_amount"] == 2468.17
    assert response["income"]["total_amount"] == 0.0
    assert response["expenses"]["main"] == [
        {"category": "Супермаркеты", "amount": 1269.94},
        {"category": "Переводы", "amount": 1198.23}
    ]
    assert response["income"]["main"] == []
