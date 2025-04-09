import json
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


def home_view(timestamp, transactions_data=None):
    current_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S") if isinstance(timestamp, str) else timestamp
    
    if transactions_data is None:
        transactions = read_transactions("data/transactions.json")
    else:
        # Если transactions_data это строка, парсим её как JSON
        if isinstance(transactions_data, str):
            transactions_data = json.loads(transactions_data)
        transactions = pd.DataFrame(transactions_data)
        transactions['Дата операции'] = pd.to_datetime(transactions['Дата операции'])
    
    # Получаем даты в формате JSON
    date_range = json.loads(get_date_range(current_time))
    start_date = datetime.strptime(date_range["start_date"], "%Y-%m-%d %H:%M:%S")
    end_date = datetime.strptime(date_range["end_date"], "%Y-%m-%d %H:%M:%S")
    
    # Получаем все данные в формате JSON
    greeting = json.loads(get_greeting(current_time))
    
    # Получаем данные о картах и транзакциях
    cards = json.loads(get_card_summaries(transactions, start_date, end_date)) if transactions is not None else []
    top_transactions = json.loads(get_top_transactions(transactions, start_date, end_date)) if transactions is not None else []
    currency_rates = json.loads(get_currency_rates()) 
    stock_prices = json.loads(get_stock_prices())
    return json.dumps({
        "greeting": greeting["greeting"],
        "date_range": date_range,
        "cards": cards,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }
)
def events_view(timestamp, transactions_data=None):
    current_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S") if isinstance(timestamp, str) else timestamp
    
    if transactions_data is None:
        transactions = read_transactions("data/transactions.json")
    else:
        # Если transactions_data это строка, парсим её как JSON
        if isinstance(transactions_data, str):
            transactions_data = json.loads(transactions_data)
        transactions = pd.DataFrame(transactions_data)
        transactions['Дата операции'] = pd.to_datetime(transactions['Дата операции'])
    
    # Получаем даты в формате JSON
    date_range = json.loads(get_date_range(current_time))
    start_date = datetime.strptime(date_range["start_date"], "%Y-%m-%d %H:%M:%S")
    end_date = datetime.strptime(date_range["end_date"], "%Y-%m-%d %H:%M:%S")
    
    filtered_transactions = transactions[
        (transactions['Дата операции'] >= start_date) &
        (transactions['Дата операции'] <= end_date)
    ].copy()
    
    expenses = filtered_transactions[filtered_transactions['Сумма операции'] < 0]
    income = filtered_transactions[filtered_transactions['Сумма операции'] > 0]
    
    # Группируем расходы по категориям
    expenses_by_category = expenses.groupby('Категория')['Сумма операции'].sum().abs()
    
    # Получаем топ-5 категорий расходов
    top_expenses = expenses_by_category.sort_values(ascending=False)
    other_expenses = pd.Series({'Остальное': top_expenses[5:].sum()}) if len(top_expenses) > 5 else pd.Series({'Остальное': 0.0})
    main_expenses = pd.concat([top_expenses[:5], other_expenses])
    
    # Группируем переводы и наличные
    transfers_and_cash = expenses[expenses['Категория'].isin(['Переводы', 'Наличные'])].groupby('Категория')['Сумма операции'].sum().abs()
    if 'Остальное' not in transfers_and_cash:
        transfers_and_cash['Остальное'] = 0.0
    
    # Группируем доходы по категориям
    income_by_category = income.groupby('Категория')['Сумма операции'].sum()
    
    # Если нет доходов, добавляем категорию "Остальное" с нулевой суммой
    income_categories = []
    if len(income_by_category) > 0:
        for cat, amt in income_by_category.sort_values(ascending=False).items():
            income_categories.append({"category": cat, "amount": round(float(amt), 2)})
    else:
        income_categories = [{"category": "Остальное", "amount": 0}]
    
    currency_rates = json.loads(get_currency_rates())
    stock_prices = json.loads(get_stock_prices())
    
    # Формируем ответ в соответствии с тестами
    return {
        "expenses": {
            "total_amount": round(abs(expenses['Сумма операции'].sum()), 2),
            "main": [
                {"category": cat, "amount": round(float(amt), 2)} 
                for cat, amt in main_expenses.items()
            ],
            "transfers_and_cash": [
                {"category": cat, "amount": round(float(amt), 2)}
                for cat, amt in transfers_and_cash.sort_values(ascending=False).items()
            ]
        },
        "income": {
            "total_amount": round(income['Сумма операции'].sum(), 2),
            "main": income_categories
        },
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
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
