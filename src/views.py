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
    result = {
        "greeting": {"greeting": "Добрый день"},
        "date_range": {"start_date": "", "end_date": ""},
        "cards": [],
        "top_transactions": [],
        "currency_rates": [],
        "stock_prices": []
    }

    try:
        # Преобразуем JSON в DataFrame
        transactions = pd.DataFrame(json.loads(transactions_json))

        # Проверяем наличие нужных колонок
        if 'Дата операции' not in transactions.columns:
            raise ValueError("Отсутствует колонка 'Дата операции'")

        # Преобразуем даты в datetime
        transactions['Дата операции'] = pd.to_datetime(transactions['Дата операции'])

        # Получаем диапазон дат
        date_range = json.loads(get_date_range(transactions))
        if date_range["start_date"] and date_range["end_date"]:
            start_date = pd.to_datetime(date_range['start_date'])
            end_date = pd.to_datetime(date_range['end_date'])
            result["date_range"] = date_range

            # Получаем данные
            current_hour = datetime.strptime(current_date, "%Y-%m-%d %H:%M:%S").hour
            result["greeting"] = json.loads(get_greeting(current_hour))
            result["cards"] = json.loads(get_card_summaries(transactions, start_date, end_date))
            result["top_transactions"] = json.loads(get_top_transactions(transactions, start_date, end_date))
            result["currency_rates"] = json.loads(get_currency_rates())
            result["stock_prices"] = json.loads(get_stock_prices())

    except Exception as e:
        print(f"Ошибка в home_view: {str(e)}")
        if "error" not in result:
            result["error"] = str(e)

    return result


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
