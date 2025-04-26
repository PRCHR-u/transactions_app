import json
from datetime import datetime

import pandas as pd
from src.utils import (
    get_greeting,
    get_date_range,
    get_card_summaries,
    get_top_transactions,
    get_currency_rates,
    get_stock_prices,
)


def home_view(current_date: str, transactions_json: str) -> dict:
    """Главное представление с общей статистикой."""
    try:
        # Преобразуем JSON в DataFrame
        transactions = pd.DataFrame(json.loads(transactions_json))

        # Проверяем наличие нужных колонок
        if 'Дата операции' not in transactions.columns:
            raise ValueError("Отсутствует колонка 'Дата операции'")

        # Получаем данные
        current_hour = datetime.strptime(current_date, "%Y-%m-%d %H:%M:%S").hour
        return {
            "greeting": json.loads(get_greeting(current_hour)),
            "date_range": json.loads(get_date_range(transactions)),
            "cards": json.loads(get_card_summaries(transactions)),
            "top_transactions": json.loads(get_top_transactions(transactions)),
            "currency_rates": json.loads(get_currency_rates()),
            "stock_prices": json.loads(get_stock_prices())
        }
    except Exception as e:
        print(f"Ошибка в home_view: {str(e)}")
        return {
            "error": str(e),
            "greeting": {"greeting": "Добрый день"},
            "date_range": {"start_date": "", "end_date": ""},
            "cards": [],
            "top_transactions": [],
            "currency_rates": [],
            "stock_prices": []
        }


def events_view(current_date: str, transactions_json: str) -> dict:
    """Представление с детальной статистикой по расходам и доходам."""
    try:
        transactions = pd.DataFrame(json.loads(transactions_json))

        # Обеспечиваем наличие нужных колонок
        if 'Сумма операции' not in transactions.columns:
            transactions['Сумма операции'] = 0.0

        # Рассчитываем расходы и доходы
        expenses_mask = transactions['Сумма операции'] < 0
        income_mask = transactions['Сумма операции'] > 0

        return {
            "expenses": {
                "total_amount": abs(transactions[expenses_mask]['Сумма операции'].sum()),
                "main": [],
                "transfers_and_cash": []
            },
            "income": {
                "total_amount": transactions[income_mask]['Сумма операции'].sum(),
                "main": []
            },
            "currency_rates": json.loads(get_currency_rates()),
            "stock_prices": json.loads(get_stock_prices())
        }
    except Exception as e:
        return {
            "error": str(e),
            "expenses": {"total_amount": 0, "main": [], "transfers_and_cash": []},
            "income": {"total_amount": 0, "main": []},
            "currency_rates": [],
            "stock_prices": []
        }
