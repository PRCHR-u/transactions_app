import json
from unittest.mock import patch
import pytest
import pandas as pd

from src.utils import get_date_range
from src.views import home_view, events_view

@pytest.fixture
def mock_functions():
    with patch('src.utils.get_greeting') as mock_greeting, \
            patch('src.utils.get_date_range') as mock_date_range, \
            patch('src.utils.get_card_summaries') as mock_cards, \
            patch('src.utils.get_top_transactions') as mock_top, \
            patch('src.utils.get_currency_rates') as mock_rates, \
            patch('src.utils.get_stock_prices') as mock_stocks, \
            patch('pandas.read_json') as mock_read_json:
        yield {
            'greeting': mock_greeting,
            'date_range': mock_date_range,
            'cards': mock_cards,
            'top': mock_top,
            'rates': mock_rates,
            'stocks': mock_stocks,
            'read_json': mock_read_json
        }

@pytest.fixture
def sample_transactions() -> pd.DataFrame:
    """Фикстура с примером данных о транзакциях."""
    data = [
        {
            "Дата операции": "2023-10-01 00:00:00",  # Добавляем время ко всем записям
            "Сумма операции": -1262.00,
            "Кешбэк": 12.62,
            "Категория": "Супермаркеты",
            "Описание": "Лента",
            "type": "expense"
        },
        {
            "Дата операции": "2023-10-10 00:00:00",
            "Сумма операции": -7.94,
            "Кешбэк": 0.08,
            "Категория": "Супермаркеты",
            "Описание": "Магнит",
            "type": "expense"
        },
        {
            "Дата операции": "2023-10-15 00:00:00",
            "Сумма операции": -1198.23,
            "Кешбэк": 11.98,
            "Категория": "Переводы",
            "Описание": "Перевод Кредитная карта. ТП 10.2 RUR",
            "type": "expense"
        },
        {
            "Дата операции": "2023-10-20 00:00:00",
            "Сумма операции": -829.00,
            "Кешбэк": 8.29,
            "Категория": "Супермаркеты",
            "Описание": "Лента",
            "type": "expense"
        },
        {
            "Дата операции": "2023-10-25 00:00:00",
            "Сумма операции": -421.00,
            "Кешбэк": 4.21,
            "Категория": "Различные товары",
            "Описание": "Ozon.ru",
            "type": "expense"
        },
        {
            "Дата операции": "2023-09-15 00:00:00",
            "Сумма операции": 14216.42,
            "Кешбэк": 0.00,
            "Категория": "Пополнение_BANK007",
            "Описание": "Пополнение счета",
            "type": "income"
        },
        {
            "Дата операции": "2023-09-20 00:00:00",
            "Сумма операции": -453.00,
            "Кешбэк": 4.53,
            "Категория": "Бонусы",
            "Описание": "Кешбэк за обычные покупки",
            "type": "expense"
        },
        {
            "Дата операции": "2023-09-25 00:00:00",
            "Сумма операции": 33000.00,
            "Кешбэк": 0.00,
            "Категория": "Пополнение_BANK007",
            "Описание": "Пополнение счета",
            "type": "income"
        },
        {
            "Дата операции": "2023-08-15 00:00:00",
            "Сумма операции": 1242.00,
            "Кешбэк": 12.42,
            "Категория": "Проценты_на_остаток",
            "Описание": "Проценты по остатку",
            "type": "income"
        },
        {
            "Дата операции": "2023-08-20 00:00:00",
            "Сумма операции": 29.00,
            "Кешбэк": 0.29,
            "Категория": "Кэшбэк",
            "Описание": "Кешбэк за обычные покупки",
            "type": "income"
        },
        {
            "Дата операции": "2023-08-25 00:00:00",
            "Сумма операции": 1000.00,
            "Кешбэк": 10.00,
            "Категория": "Переводы",
            "Описание": "Валерий А.",
            "type": "income"
        }
    ]
    df = pd.DataFrame(data)
    df['Дата операции'] = pd.to_datetime(df['Дата операции'], format='%Y-%m-%d %H:%M:%S')
    return df


@pytest.fixture
def expected(sample_transactions):
    """Фикстура с ожидаемыми результатами для тестов."""
    # Рассчитываем общие суммы расходов и доходов
    expenses = sample_transactions[sample_transactions['Сумма операции'] < 0]
    income = sample_transactions[sample_transactions['Сумма операции'] > 0]

    total_expenses = -expenses['Сумма операции'].sum()
    total_income = income['Сумма операции'].sum()

    # Финансовые данные
    financial_data = {
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

    # Данные по картам
    card_data = [
        {
            "last_digits": "3456",
            "total_spent": 1262.00,
            "cashback": 12.62
        },
        {
            "last_digits": "4321",
            "total_spent": 1198.23,
            "cashback": 11.98
        }
    ]

    # Топ транзакций (приводим даты к единому формату)
    transaction_data = [
        {
            "date": "2023-10-01",  # Было "01.10.2023"
            "amount": 1262.00,
            "category": "Супермаркеты",
            "description": "Лента"
        },
        {
            "date": "2023-10-15",  # Было "15.10.2023"
            "amount": 1198.23,
            "category": "Переводы",
            "description": "Перевод Кредитная карта. ТП 10.2 RUR"
        }
    ]

    # Диапазон дат
    dates = sample_transactions['Дата операции']
    return {
        "greeting": {"greeting": "Добрый день"},  # Словарь для сравнения
        "date_range": {
            "start_date": dates.min().strftime('%Y-%m-%d'),
            "end_date": dates.max().strftime('%Y-%m-%d')
        },
        "cards": card_data,
        "top_transactions": transaction_data,
        "currency_rates": financial_data["currency_rates"],
        "stock_prices": financial_data["stock_prices"],
        "expenses": {
            "total_amount": total_expenses,
            "main": [],
            "transfers_and_cash": []
        },
        "income": {
            "total_amount": total_income,
            "main": []
        }
    }


def test_home_view(sample_transactions, expected, mock_functions):
    # Проверяем входные данные
    print("\nПроверка sample_transactions:")
    print("Минимум дат:", sample_transactions['Дата операции'].min())
    print("Максимум дат:", sample_transactions['Дата операции'].max())

    # Настраиваем моки
    mock_functions['greeting'].return_value = json.dumps(expected['greeting'])

    # Создаём ожидаемый диапазон дат
    dates = sample_transactions['Дата операции']
    correct_date_range = {
        "start_date": dates.min().strftime('%Y-%m-%d'),
        "end_date": dates.max().strftime('%Y-%m-%d')
    }
    mock_functions['date_range'].return_value = json.dumps(correct_date_range)

    # Подготавливаем тестовые данные
    test_data = sample_transactions.copy()
    test_data['Дата операции'] = test_data['Дата операции'].dt.strftime('%Y-%m-%d %H:%M:%S')
    transactions_json = json.dumps(test_data.to_dict('records'))

    print("\nТестовые данные (первые 2 строки):")
    print(test_data.head(2).to_dict())

    # Вызываем функцию
    response = home_view("2023-10-15 14:30:00", transactions_json)

    print("\nРезультат функции:")
    print("date_range:", response['date_range'])

    # Проверяем результаты
    assert response['greeting'] == expected['greeting']
    assert response['date_range']['start_date'] == '2023-08-15', \
        f"Ожидалось: 2023-08-15, получено: {response['date_range']['start_date']}"
    assert response['date_range']['end_date'] == '2023-10-25'


def test_events_view(sample_transactions, expected, mock_functions):
    # Настраиваем моки
    mock_functions['rates'].return_value = expected['currency_rates']
    mock_functions['stocks'].return_value = expected['stock_prices']

    # Подготавливаем тестовые данные
    test_data = sample_transactions.copy()
    test_data['Дата операции'] = test_data['Дата операции'].dt.strftime('%Y-%m-%d %H:%M:%S')
    transactions_json = json.dumps(test_data.to_dict('records'))

    # Вызываем функцию
    response = events_view("2023-10-15 14:30:00", transactions_json)

    # Дебаггинг: Печать ответа для проверки
    print(json.dumps(response, indent=4))

    # Проверяем ключевые поля
    assert 'expenses' in response
    assert 'income' in response
    assert 'currency_rates' in response
    assert 'stock_prices' in response

    # Проверяем суммы расходов и доходов
    assert abs(response['expenses']['total_amount'] - expected['expenses']['total_amount']) < 0.01
    assert abs(response['income']['total_amount'] - expected['income']['total_amount']) < 0.01

    # Проверяем структуру данных
    assert isinstance(response['expenses']['main'], list)
    assert isinstance(response['expenses']['transfers_and_cash'], list)
    assert isinstance(response['income']['main'], list)

    # Проверяем курсы валют и цены акций
    assert response['currency_rates'] == expected['currency_rates']
    assert response['stock_prices'] == expected['stock_prices']


def test_sample_transactions_dates(sample_transactions):
    """Проверяем, что тестовые данные содержат корректные даты."""
    dates = sample_transactions['Дата операции']
    assert not dates.empty
    assert dates.min().strftime('%Y-%m-%d') == "2023-08-15"
    assert dates.max().strftime('%Y-%m-%d') == "2023-10-25"