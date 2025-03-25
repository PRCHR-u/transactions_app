from datetime import datetime

import pandas as pd
import pytest


def spending_by_category(df, category, date=None):
    """Расчет расходов по категории."""
    if date:
        df = df[df['Дата операции'].dt.strftime('%Y-%m-%d') <= date].copy()
    df_filtered = df[df['Категория'] == category]
    df_filtered = df_filtered[df_filtered['Сумма операции'] < 0]  # Только расходы
    category_spending = abs(df_filtered['Сумма операции'].sum())
    return {"category": category, "total": float(category_spending)}

def spending_by_weekday(df, date=None):
    """Расчет расходов по дням недели."""
    if date:
        df = df[df['Дата операции'].dt.strftime('%Y-%m-%d') <= date].copy()
    df = df[df['Сумма операции'] < 0]  # Только расходы
    weekday_spending = df.groupby(df['Дата операции'].dt.day_name())['Сумма операции'].sum().abs()
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    result = {day: float(weekday_spending.get(day, 0.0)) for day in weekdays}
    return result

def spending_by_workday(df, date=None):
    """Расчет расходов по рабочим и выходным дням."""
    if date:
        df = df[df['Дата операции'].dt.strftime('%Y-%m-%d') <= date].copy()
    df = df[df['Сумма операции'] < 0]  # Только расходы
    is_weekend = df['Дата операции'].dt.dayofweek.isin([5, 6])
    workday_spending = abs(df[~is_weekend]['Сумма операции'].sum())
    weekend_spending = abs(df[is_weekend]['Сумма операции'].sum())
    return {
        "Рабочий день": float(workday_spending),
        "Выходной день": float(weekend_spending)
    }

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

def test_spending_by_category(sample_transactions):
    result = spending_by_category(sample_transactions, "Супермаркеты", date="2023-10-15")
    assert result == {"category": "Супермаркеты", "total": 2524.0}

def test_spending_by_weekday(sample_transactions):
    result = spending_by_weekday(sample_transactions, date="2023-10-15")
    assert result == {
        "Monday": 0.0,
        "Tuesday": 0.0,
        "Wednesday": 0.0,
        "Thursday": 0.0,
        "Friday": 2524.0,
        "Saturday": 0.0,
        "Sunday": 0.0
    }

def test_spending_by_workday(sample_transactions):
    result = spending_by_workday(sample_transactions, date="2023-10-15")
    assert result == {
        "Рабочий день": 2524.0,
        "Выходной день": 0.0
    }
