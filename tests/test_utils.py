from unittest.mock import patch, Mock

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


def test_get_date_range():
    # Вызов функции
    start, end = get_date_range("2023-10-15 14:30:00")

    # Ожидаемый результат
    expected_start = datetime(2023, 10, 1, 14, 30)  # 14 дней назад
    expected_end = datetime(2023, 10, 25, 14, 30)  # 10 дней вперед

    # Проверка результата
    assert start == expected_start
    assert end == expected_end


def test_get_card_summaries():
    # Пример данных для теста
    data = {
        "Дата операции": [
            datetime(2023, 10, 15), datetime(2023, 10, 15), datetime(2023, 10, 20),
            datetime(2023, 10, 10), datetime(2023, 10, 25)
        ],
        "Номер карты": ["1234567890123456", "1234567890123456", "1234567890124321", "1234567890124321",
                        "1234567890123456"],
        "Сумма операции": [1000.0, 2210.0, 1000.0, 651.23, 1269.94],
        "Кешбэк": [10.0, 26.53, 10.0, 6.51, 12.7]
    }
    sample_transactions = pd.DataFrame(data)

    # Получение диапазона дат
    start, end = get_date_range("2023-10-15 14:30:00")

    # Вызов функции
    summaries = get_card_summaries(sample_transactions, start, end)

    # Ожидаемый результат
    expected = [
        {"last_digits": "3456", "total_spent": 4479.94, "cashback": 49.23},
        {"last_digits": "4321", "total_spent": 1651.23, "cashback": 16.51}
    ]

    # Проверка результата
    assert summaries == expected


def test_get_top_transactions():
    # Пример данных для теста
    data = {
        "Дата операции": [
            datetime(2023, 10, 15), datetime(2023, 10, 15), datetime(2023, 10, 20),
            datetime(2023, 10, 10), datetime(2023, 10, 25)
        ],
        "Сумма операции": [14216.42, 33000.0, 1198.23, 7.94, 421.0],
        "Категория": [
            "Пополнение_BANK007", "Пополнение_BANK007", "Переводы",
            "Супермаркеты", "Различные товары"
        ],
        "Описание": [
            "Пополнение счета", "Пополнение счета", "Перевод Кредитная карта. ТП 10.2 RUR",
            "Магнит", "Ozon.ru"
        ]
    }
    sample_transactions = pd.DataFrame(data)

    # Получение диапазона дат
    start, end = get_date_range("2023-10-15 14:30:00")

    # Вызов функции
    top_transactions = get_top_transactions(sample_transactions, start, end)

    # Ожидаемый результат
    expected = [
        {"date": "15.10.2023", "amount": 33000.0, "category": "Пополнение_BANK007", "description": "Пополнение счета"},
        {"date": "15.10.2023", "amount": 14216.42, "category": "Пополнение_BANK007", "description": "Пополнение счета"},
        {"date": "20.10.2023", "amount": 1198.23, "category": "Переводы",
         "description": "Перевод Кредитная карта. ТП 10.2 RUR"},
        {"date": "25.10.2023", "amount": 421.0, "category": "Различные товары", "description": "Ozon.ru"},
        {"date": "10.10.2023", "amount": 7.94, "category": "Супермаркеты", "description": "Магнит"}
    ]

    # Проверка результата
    assert top_transactions == expected


from unittest.mock import MagicMock

def test_get_currency_rates():
    # Создаем мок для fetch_data
    mock_fetch_data = MagicMock()
    mock_fetch_data.return_value = [
        {"currency": "USD", "rate": 84.7458},
        {"currency": "EUR", "rate": 91.7431}
    ]

    # Вызываем функцию с моком
    result = get_currency_rates(["USD", "EUR"], mock_fetch_data)

    # Проверяем результат
    assert result == [
        {"currency": "USD", "rate": 84.7458},
        {"currency": "EUR", "rate": 91.7431}
    ]
    mock_fetch_data.assert_called_once_with(["USD", "EUR"])  # Проверяем, что мок был вызван с правильными аргументами


def test_get_stock_prices():
    mock_fetch = Mock()
    mock_fetch.return_value = [
        {"stock": "AAPL", "price": 150.12},
        {"stock": "TSLA", "price": 1007.08}
    ]

    result = get_stock_prices(["AAPL", "TSLA"], fetch_data=mock_fetch)

    assert result == [
        {"stock": "AAPL", "price": 150.12},
        {"stock": "TSLA", "price": 1007.08}
    ]
    mock_fetch.assert_called_once_with(["AAPL", "TSLA"])

