import pandas as pd
from datetime import datetime, timedelta
import requests
import json
import logging
import os
from dotenv import load_dotenv

load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_transactions(file_path="data/operations.xls"):
    """Чтение транзакций из файла."""
    try:
        # Проверка расширения файла
        if file_path.endswith('.xlsx'):
            engine = 'openpyxl'
        elif file_path.endswith('.xls'):
            engine = 'xlrd'
        elif file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        else:
            raise ValueError("Неподдерживаемый формат файла. Используйте .xls, .xlsx или .csv.")

        df = pd.read_excel(file_path, engine=engine)
        df['Дата операции'] = pd.to_datetime(df['Дата операции'])
        df['Дата платежа'] = pd.to_datetime(df['Дата платежа'])

        # Проверка обязательных столбцов
        required_columns = ["Сумма операции", "Категория", "Дата операции"]
        for column in required_columns:
            if column not in df.columns:
                logging.warning(f"Столбец '{column}' отсутствует в данных.")
                return pd.DataFrame()

        return df
    except Exception as e:
        logging.error(f"Ошибка чтения файла: {e}")
        return pd.DataFrame()


def mock_read_transactions(file_path):
        return pd.DataFrame([
            {"Дата операции": "2023-10-01", "Сумма операции": -1262.00, "Категория": "Супермаркеты"},
            {"Дата операции": "2023-10-10", "Сумма операции": -7.94, "Категория": "Супермаркеты"},
        ])


def get_date_range(input_date_str):
    """Получение даты начала и конца периода для анализа."""
    input_date = datetime.strptime(input_date_str, "%Y-%m-%d %H:%M:%S")
    start_date = input_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return start_date, input_date

def get_greeting(hour):
    """Получение приветствия в зависимости от часа."""
    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"

def get_card_summaries(df, start_date, end_date):
    """Получение суммарных данных по картам."""
    filtered = df[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)]
    grouped = filtered.groupby("Номер карты")[["Сумма операции", "Кешбэк"]].sum().reset_index()  # Используем список
    summaries = []
    for _, row in grouped.iterrows():
        last_digits = str(row["Номер карты"])[-4:]
        total_spent = -row["Сумма операции"]
        cashback = row["Кешбэк"]
        summaries.append({
            "last_digits": last_digits,
            "total_spent": round(total_spent, 2),
            "cashback": round(cashback, 2)
        })
    return summaries

def get_top_transactions(df, start_date, end_date, top_n=5):
    """Получение топ-N транзакций по сумме платежа."""
    filtered = df[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)]
    top = filtered.nlargest(top_n, "Сумма операции")[  # Используем "Сумма операции" вместо "Сумма платежа"
        ["Дата операции", "Сумма операции", "Категория", "Описание"]
    ]
    top_transactions = []
    for _, row in top.iterrows():
        top_transactions.append({
            "date": row["Дата операции"].strftime("%d.%m.%Y"),
            "amount": round(row["Сумма операции"], 2),
            "category": row["Категория"],
            "description": row["Описание"]
        })
    return top_transactions

def get_currency_rates(currencies=["USD", "EUR"]):
    """Получение курсов валют из внешнего API."""
    api_key = os.getenv("CURRENCY_API_KEY")
    base_url = "https://api.exchangerate-api.com/v4/latest/RUB"
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        rates = response.json()["rates"]
        currency_rates = [{"currency": c, "rate": round(1 / rates[c], 4)} for c in currencies if c in rates]
        return currency_rates
    except Exception as e:
        logging.error(f"Ошибка получения курсов валют: {e}")
        return []


def get_stock_prices(stocks):
    """Получение цен на акции из внешнего API."""
    api_key = os.getenv("STOCK_API_KEY")
    base_url = "https://www.alphavantage.co/query"
    stock_prices = []
    for stock in stocks:
        try:
            params = {
                "function": "TIME_SERIES_INTRADAY",
                "symbol": stock,
                "interval": "1min",
                "apikey": api_key
            }
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()

            # Проверка наличия ключа "Time Series (1min)"
            if "Time Series (1min)" not in data:
                logging.error(f"Неверный формат ответа для акции {stock}: {data}")
                continue

            latest_time = list(data["Time Series (1min)"].keys())[0]
            price = float(data["Time Series (1min)"][latest_time]["1. open"])
            stock_prices.append({"stock": stock, "price": round(price, 2)})
        except Exception as e:
            logging.error(f"Ошибка получения цены для акции {stock}: {e}")
    return stock_prices


def summarize_expenses(df, start_date, end_date):
    """Суммирование расходов по категориям."""
    filtered = df[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date) & (df["Сумма операции"] < 0)]
    grouped = filtered.groupby("Категория")["Сумма операции"].sum().reset_index()
    grouped["Сумма операции"] = -grouped["Сумма операции"]
    main_categories = grouped.nlargest(7, "Сумма операции").to_dict("records")
    other_amount = grouped[~grouped["Категория"].isin([cat["Категория"] for cat in main_categories])]["Сумма операции"].sum()
    if other_amount > 0:
        main_categories.append({"Категория": "Остальное", "Сумма операции": round(other_amount, 2)})
    transfers_and_cash = filtered[filtered["Категория"].isin(["Наличные", "Переводы"])].groupby("Категория")["Сумма операции"].sum().reset_index()
    transfers_and_cash["Сумма операции"] = -transfers_and_cash["Сумма операции"]
    transfers_and_cash = transfers_and_cash.to_dict("records")
    total_expenses = round(filtered["Сумма операции"].sum(), 2)
    return {
        "total_amount": total_expenses,
        "main": main_categories,
        "transfers_and_cash": transfers_and_cash
    }

def summarize_income(df, start_date, end_date):
    """Суммирование поступлений по категориям."""
    filtered = df[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date) & (df["Сумма операции"] > 0)]
    grouped = filtered.groupby("Категория")["Сумма операции"].sum().reset_index()
    main_categories = grouped.nlargest(7, "Сумма операции").to_dict("records")
    total_income = round(filtered["Сумма операции"].sum(), 2)
    return {
        "total_amount": total_income,
        "main": main_categories
    }
