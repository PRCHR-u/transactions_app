import json
from datetime import datetime

import pandas as pd

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
    if isinstance(timestamp, str):
        current_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    else:
        current_time = timestamp

    if transactions_data is None:
        transactions = read_transactions("data/transactions.json")
    else:
        # Если transactions_data это строка, парсим её как JSON
        if isinstance(transactions_data, str):
            transactions_data = json.loads(transactions_data)
        transactions = pd.DataFrame(transactions_data)
        transactions['Дата операции'] = pd.to_datetime(
            transactions['Дата операции'])

    # Получаем даты в формате JSON
    date_range = json.loads(get_date_range(current_time))
    start_date = datetime.strptime(
        date_range["start_date"], "%Y-%m-%d %H:%M:%S"
        )
    end_date = datetime.strptime(date_range["end_date"], "%Y-%m-%d %H:%M:%S")

    # Получаем все данные в формате JSON
    greeting = json.loads(get_greeting(current_time))

    if transactions is not None:
        cards = json.loads(
            get_card_summaries(transactions, start_date, end_date))
        top_transactions = json.loads(
            get_top_transactions(transactions, start_date, end_date)
        )
    else:
        cards, top_transactions = [], []

    currency_rates = json.loads(get_currency_rates())
    stock_prices = json.loads(get_stock_prices())

    data = {
        "greeting": greeting["greeting"],
        "date_range": date_range,
        "cards": cards,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }
    return data


def events_view(timestamp, transactions_data=None):
    current_time = (
        datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        if isinstance(timestamp, str)
        else timestamp
    )

    if transactions_data is None:
        transactions = read_transactions("data/transactions.json")
    else:
        # Если transactions_data это строка, парсим её как JSON
        if isinstance(transactions_data, str):
            transactions_data = json.loads(transactions_data)

        transactions = pd.DataFrame(transactions_data)
        transactions["Дата операции"] = pd.to_datetime(
            transactions["Дата операции"]
        )

    # Получаем даты в формате JSON
    date_range = json.loads(get_date_range(current_time))
    start_date = datetime.strptime(
        date_range["start_date"], "%Y-%m-%d %H:%M:%S"
        )
    end_date = datetime.strptime(date_range["end_date"], "%Y-%m-%d %H:%M:%S")

    filtered_transactions = transactions[
        (transactions["Дата операции"] >= start_date)
        & (transactions["Дата операции"] <= end_date)
    ].copy()

    expenses = filtered_transactions[
        filtered_transactions["Сумма операции"] < 0]
    income = filtered_transactions[filtered_transactions["Сумма операции"] > 0]

    # Группируем расходы по категориям
    expenses_by_category = expenses.groupby(
        'Категория'
        )['Сумма операции'].sum().abs()

    # Получаем топ-5 категорий расходов
    top_expenses = expenses_by_category.sort_values(ascending=False)

    # Группируем переводы и наличные
    transfers_and_cash = (
        expenses[expenses["Категория"].isin(["Переводы", "Наличные"])]
        .groupby("Категория")["Сумма операции"]
        .sum()
        .abs()
    )

    # Группируем доходы по категориям
    income_by_category = income.groupby("Категория")["Сумма операции"].sum()

    currency_rates = json.loads(get_currency_rates())
    stock_prices = json.loads(
        get_stock_prices()
        )

    main_expenses = pd.concat([
        top_expenses[:5],
        pd.Series({'Остальное': top_expenses[5:].sum()})
        if len(top_expenses) > 5 else pd.Series({'Остальное': 0.0})
    ])

    return {
        "expenses": {
            "total_amount": round(abs(expenses["Сумма операции"].sum()), 2),
            "main": [
                {"category": cat, "amount": round(float(amt), 2)}
                for cat, amt in main_expenses.items()
            ],
            "transfers_and_cash": [
                {"category": cat, "amount": round(float(amt), 2)}
                for cat, amt in transfers_and_cash.sort_values(
                    ascending=False
                ).items()
            ]
        },
        "income": {
            "total_amount": round(income["Сумма операции"].sum(), 2),
            "main": [
                {
                    "category": cat,
                    "amount": round(float(amt), 2),
                }
                for cat, amt in income_by_category.sort_values(
                    ascending=False
                ).items()
            ]
            if not income_by_category.empty
            else [{"category": "Остальное", "amount": 0}],
        },
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }


def categories_view(timestamp, transactions_data=None):
    current_time = (
        datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        if isinstance(timestamp, str)
        else timestamp
    )

    if transactions_data is None:
        transactions = read_transactions("data/transactions.json")
    else:
        if isinstance(transactions_data, str):
            transactions_data = json.loads(transactions_data)
        transactions = pd.DataFrame(transactions_data)
        transactions["Дата операции"] = pd.to_datetime(
            transactions["Дата операции"]
        )
    date_range = json.loads(get_date_range(current_time))
    start_date = datetime.strptime(
        date_range["start_date"], "%Y-%m-%d %H:%M:%S"
        )
    end_date = datetime.strptime(date_range["end_date"], "%Y-%m-%d %H:%M:%S")

    filtered_transactions = transactions[
        (transactions["Дата операции"] >= start_date)
        & (transactions["Дата операции"] <= end_date)
    ].copy()

    expenses = filtered_transactions[
        filtered_transactions["Сумма операции"] < 0]
    income = filtered_transactions[filtered_transactions["Сумма операции"] > 0]

    transfers_and_cash = (
        expenses[
            expenses["Категория"].isin(["Переводы", "Наличные"])
        ]
        .groupby("Категория")["Сумма операции"]
        .sum()
        .abs()
    )
    income_by_category = income.groupby("Категория")["Сумма операции"].sum()

    income_categories = [
        {"category": cat, "amount": round(float(amt), 2)}
        for cat, amt in income_by_category.sort_values(
            ascending=False
        ).items()
    ]
    if not income_categories:
        income_categories = [{"category": "Остальное", "amount": 0}]

    return {
        "expenses": {
            "total_amount": round(abs(expenses["Сумма операции"].sum()), 2),
            "transfers_and_cash": [
                {"category": cat, "amount": round(float(amt), 2)}
                for cat, amt in transfers_and_cash.sort_values(
                    ascending=False
                ).items()
            ],
        },
        "income": {
            "total_amount": round(
                income["Сумма операции"].sum(), 2
            ),
            "main": income_categories},
    }
