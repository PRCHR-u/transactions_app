from unittest.mock import MagicMock

import pandas as pd
import pytest


@pytest.fixture
def sample_transactions():
    data = {
        "Дата операции": [
            "2023-10-01 12:00:00",
            "2023-10-10 15:00:00",
            "2023-10-15 14:30:00",
            "2023-10-20 10:00:00",
            "2023-10-25 18:00:00",
            "2023-09-15 12:00:00",
            "2023-09-20 15:00:00",
            "2023-09-25 14:30:00",
            "2023-08-15 12:00:00",
            "2023-08-20 15:00:00",
            "2023-08-25 14:30:00",
        ],
        "Номер карты": [
            "1234567890123456",
            "1234567890123456",
            "6543210987654321",
            "6543210987654321",
            "1234567890123456",
            "1234567890123456",
            "6543210987654321",
            "6543210987654321",
            "1234567890123456",
            "6543210987654321",
            "1234567890123456",
        ],
        "Сумма операции": [
            -1262.00,
            -7.94,
            -1198.23,
            -829.00,
            -421.00,
            14216.42,
            -453.00,
            33000.00,
            1242.00,
            29.00,
            1000.00,
        ],
        "Кешбэк": [
            12.62, 0.08, 11.98, 8.29,
            4.21, 0.00, 4.53, 0.00,
            12.42, 0.29, 10.00
            ],
        "Категория": [
            "Супермаркеты",
            "Супермаркеты",
            "Переводы",
            "Супермаркеты",
            "Различные товары",
            "Пополнение_BANK007",
            "Бонусы",
            "Пополнение_BANK007",
            "Проценты_на_остаток",
            "Кэшбэк",
            "Переводы",
        ],
        "Описание": [
            "Лента",
            "Магнит",
            "Перевод Кредитная карта. ТП 10.2 RUR",
            "Лента",
            "Ozon.ru",
            "Пополнение счета",
            "Кешбэк за обычные покупки",
            "Пополнение счета",
            "Проценты по остатку",
            "Кешбэк за обычные покупки",
            "Валерий А.",
        ],
    }
    df = pd.DataFrame(data)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"])
    return df


@pytest.fixture
def sample_user_settings():
    return {
        "user_currencies": ["USD", "EUR"],
        "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"],
    }


@pytest.fixture
def mock_currency_rates_response(monkeypatch):
    mock_response = {
        "rates": {"USD": 73.21, "EUR": 87.08, "RUB": 1.0}
    }
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = mock_response
    monkeypatch.setattr("requests.get", lambda *args, **kwargs: mock)
    return mock_response


@pytest.fixture
def mock_stock_prices_response(monkeypatch):
    mock_response = {
        "Time Series (1min)": {
            "2023-10-15 14:30:00": {"1. open": "150.12"},
            "2023-10-15 14:31:00": {"1. open": "3173.18"},
            "2023-10-15 14:32:00": {"1. open": "2742.39"},
            "2023-10-15 14:33:00": {"1. open": "296.71"},
            "2023-10-15 14:34:00": {"1. open": "1007.08"},
        }
    }
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = mock_response
    monkeypatch.setattr("requests.get", lambda *args, **kwargs: mock)
    return mock_response
