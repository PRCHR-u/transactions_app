from unittest.mock import patch

import pandas as pd

from src.utils import (
    read_transactions,
    get_currency_rates,
    get_stock_prices
)


def events_view(date, read_transactions, get_currency_rates, get_stock_prices):
    """
    Возвращает данные о расходах и доходах на основе транзакций.

    Args:
        date (str): Дата для фильтрации транзакций (в данном примере не используется).
        read_transactions: Функция для чтения транзакций.
        get_currency_rates: Функция для получения курсов валют.
        get_stock_prices: Функция для получения цен акций.

    Returns:
        dict: Словарь с данными о расходах и доходах.
    """
    transactions = read_transactions()
    expenses = calculate_expenses(transactions)
    income = calculate_income(transactions)

    return {
        "expenses": {
            "total_amount": expenses
        },
        "income": income
    }


def calculate_expenses(transactions: pd.DataFrame):
    """
    Вычисляет общую сумму расходов из DataFrame транзакций.

    Args:
        transactions (pd.DataFrame): DataFrame, содержащий информацию о транзакциях.

    Returns:
        float: Общая сумма расходов.
    """
    if "Сумма операции" not in transactions.columns:
        raise ValueError("Столбец 'Сумма операции' отсутствует в данных.")

    transactions["Сумма операции"] = pd.to_numeric(transactions["Сумма операции"], errors='coerce')
    expenses = transactions[transactions["Сумма операции"] < 0]
    return expenses["Сумма операции"].sum()


def calculate_income(transactions):
    """
    Рассчитывает доходы.
    """
    if transactions.empty:
        return {"total_amount": 0, "main": []}

    if "Сумма операции" not in transactions.columns:
        raise ValueError("Столбец 'Сумма операции' отсутствует в данных.")

    income = transactions[transactions["Сумма операции"] > 0]
    total_amount = income["Сумма операции"].sum()
    main_categories = income.groupby("Категория")["Сумма операции"].sum().reset_index()
    main_categories = main_categories.rename(columns={"Сумма операции": "amount"})
    main_categories = main_categories.to_dict("records")
    return {"total_amount": total_amount, "main": main_categories}
