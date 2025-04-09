import json
import re
import logging
from datetime import datetime

import numpy as np
import pandas as pd
import pytest


def profitable_categories(df, year, month):
    """Расчет расходов по категориям за указанный месяц."""
    df['Дата операции'] = pd.to_datetime(df['Дата операции'])
    mask = (df['Дата операции'].dt.year == year) & (df['Дата операции'].dt.month == month)
    filtered_df = df[mask].copy()
    filtered_df = filtered_df[filtered_df['Сумма операции'] < 0]  # Только расходы
    filtered_df['Сумма операции'] = filtered_df['Сумма операции'].abs()
    
    # Группируем по категориям и суммируем расходы
    category_totals = filtered_df.groupby('Категория')['Сумма операции'].sum()
    
    # Определяем все возможные категории
    all_categories = [
        "Супермаркеты", "Переводы", "Различные товары", "Бонусы",
        "Пополнение_BANK007", "Проценты_на_остаток", "Кэшбэк"
    ]
    
    # Формируем словарь с суммами по категориям
    result = {cat: float(category_totals.get(cat, 0.0)) for cat in all_categories}
    
    # Сериализуем результат в JSON-строку
    return json.dumps(result, ensure_ascii=False)

def investment_bank(month, transactions, threshold):
    """Расчет суммы для Инвесткопилки за указанный месяц."""
    df = pd.DataFrame(transactions)
    df['Дата операции'] = pd.to_datetime(df['Дата операции'])
    mask = df['Дата операции'].dt.strftime('%Y-%m') == month
    filtered_df = df[mask & (df['Сумма операции'] < 0)].copy()
    
    if len(filtered_df) == 0:
        return json.dumps(0.0)
    
    # Берем первую транзакцию и округляем её
    amount = abs(filtered_df.iloc[0]['Сумма операции'])
    rounded = np.ceil(amount / threshold) * threshold
    difference = rounded - amount
    
    return json.dumps(round(float(difference), 2))

def simple_search(query, transactions):
    """Поиск транзакций по категории и описанию."""
    query = query.lower()
    matches = [
        t for t in transactions 
        if query in t['Категория'].lower() or query in t['Описание'].lower()
    ]
    return json.dumps(matches, ensure_ascii=False)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def search_phone_numbers(transactions):
    """Поиск транзакций с номерами телефонов в описании."""
    logging.info("Вызвана функция search_phone_numbers")
    try:
        # Паттерн для поиска номеров в форматах:
        # +7 921 11-22-33
        # +7 995 555-55-55
        # +7 981 333-44-55
        phone_pattern = r'\+7\s+\d{3}\s+\d{2,3}[-\s]\d{2}[-\s]\d{2}'
        matches = [
            t for t in transactions
            if re.search(phone_pattern, t['Описание'])
        ]
        return json.dumps(matches, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Ошибка в функции search_phone_numbers: {e}")
        return json.dumps([], ensure_ascii=False)

def search_physical_transfers(transactions):
    """Поиск транзакций в категории 'Переводы'."""
    # Паттерн для исключения технических переводов (на карту, счет и т.д.)
    exclude_pattern = re.compile(r'карт|счет|кредитн|перевод|тп', re.IGNORECASE)
    # Паттерн для имени (1-2 слова, возможно с инициалами)
    name_pattern = re.compile(r'^[А-ЯA-Z][а-яa-z]+(?:\s+[А-ЯA-Z]\.?)?$|^[А-ЯA-Z][а-яa-z]+\s+[А-ЯA-Z][а-яa-z]+$')
    
    matches = [
        t for t in transactions 
        if t['Категория'] == 'Переводы' 
        and not exclude_pattern.search(t['Описание'].lower())
        and name_pattern.match(t['Описание'])
    ]
    return json.dumps(matches, ensure_ascii=False)

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
    assert result == "38.00"

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
