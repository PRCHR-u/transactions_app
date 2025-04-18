import json
import logging
import os
from datetime import datetime

import pandas as pd
import requests
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def read_transactions(file_path="data/transactions.json"):
    """Чтение транзакций из JSON-файла."""
    try:
        if file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            df = pd.DataFrame(data)
        else:
            df = pd.read_excel(file_path)
        
        df['Дата операции'] = pd.to_datetime(df['Дата операции'])
        return df
    except Exception as e:
        logging.error(f"Ошибка чтения файла: {e}")
        return pd.DataFrame()


def get_date_range(input_date):
    """Получение даты начала и конца периода для анализа."""
    logging.info("Вызвана функция get_date_range")
    if isinstance(input_date, str): 
        input_date = datetime.strptime(input_date, "%Y-%m-%d %H:%M:%S") 
    start_date = input_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return json.dumps({
        "start_date": start_date.strftime("%Y-%m-%d %H:%M:%S"),
        "end_date": input_date.strftime("%Y-%m-%d %H:%M:%S")
    })



def get_greeting(self):
    """Получение приветствия в зависимости от часа."""
    logging.info("Вызвана функция get_greeting")
    try:
        current_hour = datetime.now().hour
        if 5 <= current_hour < 12:
            greeting = "Доброе утро"
        elif 12 <= current_hour < 18:
            greeting = "Добрый день"
        elif 18 <= current_hour < 23:
            greeting = "Добрый вечер"
        else:
            greeting = "Доброй ночи"
    except Exception as e:
        logging.error(f"Ошибка в функции get_greeting: {e}")
        greeting = "Ошибка получения приветствия"
    return json.dumps({"greeting": greeting})


def get_card_summaries(transactions, start_date, end_date):
    """Получение суммарных данных по картам."""
    logging.info("Вызвана функция get_card_summaries")
    try:
        filtered_transactions = transactions[
            (transactions['Дата операции'] >= start_date) &
            (transactions['Дата операции'] <= end_date)
        ]
        card_summaries = []
        for card in filtered_transactions['Номер карты'].dropna().unique():  # Исправлено здесь
            card_transactions = filtered_transactions[
                filtered_transactions['Номер карты'] == card
                ]
            total_spent = abs(card_transactions[
                                 card_transactions['Сумма операции'] < 0
                                 ]['Сумма операции'].sum())
            total_cashback = card_transactions['Кэшбэк'].sum()
            card_summaries.append({
                "last_digits": card[-4:],
                "total_spent": round(float(total_spent), 2),
                "cashback": round(float(total_cashback), 2)
            })
        return json.dumps(
            sorted(card_summaries, key=lambda x: (-x["total_spent"], x["last_digits"]))
            )
    except Exception as e:
        logging.error(f"Ошибка в функции get_card_summaries: {e}")
        return json.dumps([])

def get_top_transactions(transactions, start_date, end_date):
    """Получение топ транзакций по сумме операции."""
    logging.info("Вызвана функция get_top_transactions")
    try:
        filtered_transactions = transactions[
            (transactions['Дата операции'] >= start_date) &
            (transactions['Дата операции'] <= end_date) &
            (transactions['Сумма операции'] < 0)
            ].sort_values('Сумма операции', ascending=True)

        top_transactions = []  # Initialize an empty list
        for _, row in filtered_transactions.iterrows():
            top_transactions.append({
                "date": row['Дата операции'].strftime('%d.%m.%Y'),
                "amount": round(float(abs(row['Сумма операции'])), 2),
                "category": row['Категория'],
                "description": row['Описание']
            })
        return json.dumps(
            sorted(top_transactions, key=lambda x: (-x["amount"], x["date"]))
            )
    except Exception as e:
        logging.error(f"Ошибка в функции get_top_transactions: {e}")
        return json.dumps([])

def get_currency_rates(currencies=None):
    """Получение курсов валют из user_settings.json."""
    logging.info("Вызвана функция get_currency_rates")
    try:
        with open("user_settings.json", "r") as f:
            user_settings = json.load(f)
            currencies = user_settings.get("user_currencies", ["USD", "EUR"])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Ошибка при чтении user_settings.json: {e}")
        currencies = ["USD", "EUR"]  # Default currencies

    url = os.getenv("CURRENCY_API_URL")  # Используем URL из .env
    if not url:
        raise ValueError(
            "Currency API URL not found in environment variables"
            )
    response = requests.get(url)
    response.raise_for_status()

    data = response.json()
    
    rates = [{"currency": currency, "rate": data["rates"].get(currency, 0)} for currency in currencies]
    return json.dumps(rates)

def get_stock_prices(stocks=None):
    """Получение цен акций."""
    logging.info("Вызвана функция get_stock_prices")
    try:
        if stocks is None:
            stocks = ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]

        stock_data = yf.download(stocks, period="1d", progress=False)
        if stock_data.empty:
            raise ValueError(
                "No stock data received from Yahoo Finance API"
                )

        prices = [
            {
                "stock": stock,
                "price": round(
                    stock_data["Close"][stock].iloc[-1], 2
                    )
                }
            for stock in stocks
            ]

        return json.dumps(prices)
    except Exception as e:
        logging.error(f"Ошибка в функции get_stock_prices: {e}")
        return json.dumps([])

def summarize_expenses(df, start_date, end_date):
    """Суммирование расходов по категориям."""
    filtered = df[
        (df["Дата операции"] >= start_date) &
        (df["Дата операции"] <= end_date) &
        (df["Сумма операции"] < 0)
        ]
    grouped = (
        filtered.groupby("Категория")["Сумма операции"]
        .sum()
        .reset_index()
        )
    grouped["Сумма операции"] = -grouped["Сумма операции"]
    main_categories = (
        grouped.nlargest(7, "Сумма операции")
        .to_dict("records")
        )
    other_amount = grouped[
        ~grouped["Категория"].isin([cat["Категория"] for cat in main_categories])
        ]["Сумма операции"].sum()
    if other_amount > 0:
        main_categories.append(
            {
                "Категория": "Остальное",
                "Сумма операции": round(other_amount, 2)
                }
            )
    transfers_and_cash = (
        filtered[filtered["Категория"].isin(["Наличные", "Переводы"])]
        .groupby("Категория")["Сумма операции"]
        .sum()
        .reset_index()
        )
    transfers_and_cash["Сумма операции"] = -transfers_and_cash["Сумма операции"]
    transfers_and_cash = transfers_and_cash.to_dict("records")
    total_expenses = round(filtered["Сумма операции"].sum(), 2)
    return {
        "total_amount": total_expenses, "main": main_categories,
        "transfers_and_cash": transfers_and_cash
        }


def summarize_income(df, start_date, end_date):
    """Суммирование поступлений по категориям."""
    filtered = df[
        (df["Дата операции"] >= start_date) &
        (df["Дата операции"] <= end_date) &
        (df["Сумма операции"] > 0)
        ]
    grouped = (
        filtered.groupby("Категория")["Сумма операции"]
        .sum()
        .reset_index()
        )
    main_categories = (
        grouped.nlargest(7, "Сумма операции")
        .to_dict("records")
        )
    total_income = round(filtered["Сумма операции"].sum(), 2)
    return {
        "total_amount": total_income, "main": main_categories
        }
