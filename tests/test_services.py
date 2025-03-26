import json

import pandas as pd
import pytest

from src.services import (
    investment_bank,
    profitable_categories,
    search_phone_numbers,
    search_physical_transfers,
    simple_search,
)


@pytest.fixture
def sample_transactions():
    data = [
        {
            "Дата операции": "2023-10-01",
            "Сумма операции": -1262.00,
            "Кешбэк": 12.62,
            "Категория": "Супермаркеты",
            "Описание": "Лента"
        },
        {
            "Дата операции": "2023-10-10",
            "Сумма операции": -7.94,
            "Кешбэк": 0.08,
            "Категория": "Супермаркеты",
            "Описание": "Магнит"
        },
        {
            "Дата операции": "2023-10-15",
            "Сумма операции": -1198.23,
            "Кешбэк": 11.98,
            "Категория": "Переводы",
            "Описание": "Перевод Кредитная карта. ТП 10.2 RUR"
        },
        {
            "Дата операции": "2023-10-20",
            "Сумма операции": -829.00,
            "Кешбэк": 8.29,
            "Категория": "Супермаркеты",
            "Описание": "Лента"
        },
        {
            "Дата операции": "2023-10-25",
            "Сумма операции": -421.00,
            "Кешбэк": 4.21,
            "Категория": "Различные товары",
            "Описание": "Ozon.ru"
        },
        {
            "Дата операции": "2023-09-15",
            "Сумма операции": 14216.42,
            "Кешбэк": 0.00,
            "Категория": "Пополнение_BANK007",
            "Описание": "Пополнение счета"
        },
        {
            "Дата операции": "2023-09-20",
            "Сумма операции": -453.00,
            "Кешбэк": 4.53,
            "Категория": "Бонусы",
            "Описание": "Кешбэк за обычные покупки"
        },
        {
            "Дата операции": "2023-09-25",
            "Сумма операции": 33000.00,
            "Кешбэк": 0.00,
            "Категория": "Пополнение_BANK007",
            "Описание": "Пополнение счета"
        },
        {
            "Дата операции": "2023-08-15",
            "Сумма операции": 1242.00,
            "Кешбэк": 12.42,
            "Категория": "Проценты_на_остаток",
            "Описание": "Проценты по остатку"
        },
        {
            "Дата операции": "2023-08-20",
            "Сумма операции": 29.00,
            "Кешбэк": 0.29,
            "Категория": "Кэшбэк",
            "Описание": "Кешбэк за обычные покупки"
        },
        {
            "Дата операции": "2023-08-25",
            "Сумма операции": 1000.00,
            "Кешбэк": 10.00,
            "Категория": "Переводы",
            "Описание": "Валерий А."
        }
    ]
    return data


def test_profitable_categories(sample_transactions):
    result = profitable_categories(pd.DataFrame(sample_transactions), 2023, 10)
    expected = {
        "Супермаркеты": 2098.94,
        "Переводы": 1198.23,
        "Различные товары": 421.0,
        "Бонусы": 0.0,
        "Пополнение_BANK007": 0.0,
        "Проценты_на_остаток": 0.0,
        "Кэшбэк": 0.0
    }
    assert result == json.dumps(expected, ensure_ascii=False)


def test_investment_bank(sample_transactions):
    result = investment_bank("2023-10", sample_transactions, 50)
    # Проверяем округление первой транзакции: 1262 -> 1300 (разница 38)
    assert result == "38.0"


def test_simple_search(sample_transactions):
    # Тест поиска по категории
    result = simple_search("Супермаркеты", sample_transactions)
    expected = [
        {
            "Дата операции": "2023-10-01",
            "Сумма операции": -1262.00,
            "Кешбэк": 12.62,
            "Категория": "Супермаркеты",
            "Описание": "Лента"
        },
        {
            "Дата операции": "2023-10-10",
            "Сумма операции": -7.94,
            "Кешбэк": 0.08,
            "Категория": "Супермаркеты",
            "Описание": "Магнит"
        },
        {
            "Дата операции": "2023-10-20",
            "Сумма операции": -829.00,
            "Кешбэк": 8.29,
            "Категория": "Супермаркеты",
            "Описание": "Лента"
        }
    ]
    assert result == json.dumps(expected, ensure_ascii=False)

    # Тест поиска по описанию
    result = simple_search("Лента", sample_transactions)
    expected = [
        {
            "Дата операции": "2023-10-01",
            "Сумма операции": -1262.00,
            "Кешбэк": 12.62,
            "Категория": "Супермаркеты",
            "Описание": "Лента"
        },
        {
            "Дата операции": "2023-10-20",
            "Сумма операции": -829.00,
            "Кешбэк": 8.29,
            "Категория": "Супермаркеты",
            "Описание": "Лента"
        }
    ]
    assert result == json.dumps(expected, ensure_ascii=False)


def test_search_phone_numbers(sample_transactions):
    # Добавляем транзакции с номерами телефонов
    transactions = sample_transactions + [
        {
            "Дата операции": "2023-10-05",
            "Сумма операции": -100.00,
            "Кешбэк": 1.00,
            "Категория": "Мобильная связь",
            "Описание": "Я МТС +7 921 11-22-33"
        },
        {
            "Дата операции": "2023-10-06",
            "Сумма операции": -200.00,
            "Кешбэк": 2.00,
            "Категория": "Мобильная связь",
            "Описание": "Тинькофф Мобайл +7 995 555-55-55"
        },
        {
            "Дата операции": "2023-10-07",
            "Сумма операции": -300.00,
            "Кешбэк": 3.00,
            "Категория": "Мобильная связь",
            "Описание": "МТС Mobile +7 981 333-44-55"
        }
    ]
    
    result = search_phone_numbers(transactions)
    expected = [
        {
            "Дата операции": "2023-10-05",
            "Сумма операции": -100.00,
            "Кешбэк": 1.00,
            "Категория": "Мобильная связь",
            "Описание": "Я МТС +7 921 11-22-33"
        },
        {
            "Дата операции": "2023-10-06",
            "Сумма операции": -200.00,
            "Кешбэк": 2.00,
            "Категория": "Мобильная связь",
            "Описание": "Тинькофф Мобайл +7 995 555-55-55"
        },
        {
            "Дата операции": "2023-10-07",
            "Сумма операции": -300.00,
            "Кешбэк": 3.00,
            "Категория": "Мобильная связь",
            "Описание": "МТС Mobile +7 981 333-44-55"
        }
    ]
    assert result == json.dumps(expected, ensure_ascii=False)


def test_search_physical_transfers(sample_transactions):
    # Добавляем разные типы переводов
    transactions = sample_transactions + [
        {
            "Дата операции": "2023-10-16",
            "Сумма операции": -500.00,
            "Кешбэк": 5.00,
            "Категория": "Переводы",
            "Описание": "Перевод на карту 1234"
        },
        {
            "Дата операции": "2023-10-17",
            "Сумма операции": -1000.00,
            "Кешбэк": 10.00,
            "Категория": "Переводы",
            "Описание": "Перевод на счет 5678"
        },
        {
            "Дата операции": "2023-10-18",
            "Сумма операции": -2000.00,
            "Кешбэк": 20.00,
            "Категория": "Переводы",
            "Описание": "Иван Петров"
        }
    ]
    
    result = search_physical_transfers(transactions)
    expected = [
        {
            "Дата операции": "2023-08-25",
            "Сумма операции": 1000.00,
            "Кешбэк": 10.00,
            "Категория": "Переводы",
            "Описание": "Валерий А."
        },
        {
            "Дата операции": "2023-10-18",
            "Сумма операции": -2000.00,
            "Кешбэк": 20.00,
            "Категория": "Переводы",
            "Описание": "Иван Петров"
        }
    ]
    assert result == json.dumps(expected, ensure_ascii=False)
