from datetime import datetime

import pandas as pd
import pytest


def profitable_categories(df, year, month):
    """Расчет расходов по категориям за указанный месяц."""
    df['Дата операции'] = pd.to_datetime(df['Дата операции'])
    mask = (df['Дата операции'].dt.year == year) & (df['Дата операции'].dt.month == month)
    filtered_df = df[mask].copy()
    filtered_df = filtered_df[filtered_df['Сумма операции'] < 0]  # Только расходы
    filtered_df['Сумма операции'] = filtered_df['Сумма операции'].abs()
    category_totals = filtered_df.groupby('Категория')['Сумма операции'].sum().to_dict()
    
    # Добавляем категории с нулевыми значениями
    all_categories = [
        "Супермаркеты", "Переводы", "Различные товары", "Бонусы",
        "Пополнение_BANK007", "Проценты_на_остаток", "Кэшбэк"
    ]
    return {cat: float(category_totals.get(cat, 0.0)) for cat in all_categories}

def investment_bank(month, transactions, threshold):
    """Расчет суммы кэшбэка за указанный месяц."""
    df = pd.DataFrame(transactions)
    df['Дата операции'] = pd.to_datetime(df['Дата операции'])
    mask = df['Дата операции'].dt.strftime('%Y-%m') == month
    filtered_df = df[mask].copy()
    total_cashback = filtered_df['Кешбэк'].sum()
    return float(total_cashback)

def simple_search(query, transactions):
    """Поиск транзакций по категории."""
    return [t for t in transactions if query.lower() in t['Категория'].lower()]

def search_phone_numbers(transactions):
    """Поиск транзакций с номерами телефонов в описании."""
    import re
    phone_pattern = r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    return [t for t in transactions if re.search(phone_pattern, t['Описание'])]

def search_physical_transfers(transactions):
    """Поиск транзакций в категории 'Переводы'."""
    return [t for t in transactions if t['Категория'] == 'Переводы']

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
    assert result == {
        "Супермаркеты": 2524.0,
        "Переводы": 1198.23,
        "Различные товары": 421.0,
        "Бонусы": 453.0,
        "Пополнение_BANK007": 0.0,
        "Проценты_на_остаток": 0.0,
        "Кэшбэк": 0.0
    }

def test_investment_bank(sample_transactions):
    result = investment_bank("2023-10", sample_transactions, 50)
    assert result == 38.0

def test_simple_search(sample_transactions):
    result = simple_search("Супермаркеты", sample_transactions)
    assert result == [
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

def test_search_phone_numbers(sample_transactions):
    result = search_phone_numbers(sample_transactions)
    assert result == []

def test_search_physical_transfers(sample_transactions):
    result = search_physical_transfers(sample_transactions)
    assert result == [
        {
            "Дата операции": "2023-10-15",
            "Сумма операции": -1198.23,
            "Кешбэк": 11.98,
            "Категория": "Переводы",
            "Описание": "Перевод Кредитная карта. ТП 10.2 RUR"
        },
        {
            "Дата операции": "2023-08-25",
            "Сумма операции": 1000.00,
            "Кешбэк": 10.00,
            "Категория": "Переводы",
            "Описание": "Валерий А."
        }
    ]
