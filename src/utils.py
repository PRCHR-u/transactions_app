import json
import logging
import os
from datetime import datetime, timedelta

import pandas as pd
import requests
from dotenv import load_dotenv
import yfinance as yf

load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_transactions(file_path="data/transactions.json"):
    """Чтение транзакций из JSON-файла."""
    try:
        if file_path.endswith('.json'):
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


def get_date_range(transactions: pd.DataFrame) -> str:
    """Возвращает диапазон дат транзакций в формате JSON."""
    try:
        if not transactions.empty and 'Дата операции' in transactions.columns:
            # Преобразуем даты в datetime, если они еще не в этом формате
            if not pd.api.types.is_datetime64_any_dtype(transactions['Дата операции']):
                transactions['Дата операции'] = pd.to_datetime(
                    transactions['Дата операции'],
                    format='%Y-%m-%d %H:%M:%S',
                    errors='coerce'
                )
            
            # Удаляем некорректные даты
            valid_dates = transactions[transactions['Дата операции'].notna()]
            if not valid_dates.empty:
                return json.dumps({
                    "start_date": valid_dates['Дата операции'].min().strftime('%Y-%m-%d'),
                    "end_date": valid_dates['Дата операции'].max().strftime('%Y-%m-%d')
                })
    except Exception as e:
        print(f"Ошибка в get_date_range: {str(e)}")
    return json.dumps({"start_date": "", "end_date": ""})


def get_greeting(hour: int) -> str:
    """Возвращает приветствие в зависимости от времени дня."""
    if 5 <= hour < 12:
        return json.dumps({"greeting": "Доброе утро"})
    elif 12 <= hour < 18:
        return json.dumps({"greeting": "Добрый день"})
    elif 18 <= hour < 23:
        return json.dumps({"greeting": "Добрый вечер"})
    else:
        return json.dumps({"greeting": "Доброй ночи"})


def get_card_summaries(transactions, start_date, end_date):
    """Получение суммарных данных по картам."""
    try:
        filtered_transactions = transactions[
            (transactions['Дата операции'] >= start_date) &
            (transactions['Дата операции'] <= end_date)
        ]
        
        # Если нет колонки 'Номер карты', возвращаем пустой список
        if 'Номер карты' not in filtered_transactions.columns:
            return json.dumps([])
        
        card_summaries = []
        for card in filtered_transactions['Номер карты'].unique():
            card_transactions = filtered_transactions[filtered_transactions['Номер карты'] == card]
            total_spent = abs(card_transactions[card_transactions['Сумма операции'] < 0]['Сумма операции'].sum())
            total_cashback = card_transactions['Кешбэк'].sum()
            card_summaries.append({
                "last_digits": card[-4:],
                "total_spent": round(float(total_spent), 2),
                "cashback": round(float(total_cashback), 2)
            })
        
        return json.dumps(sorted(card_summaries, key=lambda x: (-x["total_spent"], x["last_digits"])))
    except Exception as e:
        print(f"Ошибка в get_card_summaries: {str(e)}")
        return json.dumps([])


def get_top_transactions(transactions, start_date, end_date):
    """Получение топ транзакций по сумме операции."""
    filtered_transactions = transactions[
        (transactions['Дата операции'] >= start_date) &
        (transactions['Дата операции'] <= end_date) &
        (transactions['Сумма операции'] < 0)
    ].sort_values('Сумма операции', ascending=True)
    
    top_transactions = []
    for _, row in filtered_transactions.iterrows():
        top_transactions.append({
            "date": row['Дата операции'].strftime('%d.%m.%Y'),
            "amount": round(float(abs(row['Сумма операции'])), 2),
            "category": row['Категория'],
            "description": row['Описание']
        })
    
    return json.dumps(sorted(top_transactions, key=lambda x: (-x["amount"], x["date"])))


def get_currency_rates() -> str:
    """Возвращает текущие курсы валют (стоимость валюты в рублях)."""
    try:
        # В реальном приложении здесь был бы запрос к API
        rates = [
            {"currency": "USD", "rate": 82.45},  # 1 USD = 82.45 RUB
            {"currency": "EUR", "rate": 94.20}   # 1 EUR = 94.20 RUB
        ]
        return json.dumps(rates)
    except Exception as e:
        logging.error(f"Ошибка в get_currency_rates: {str(e)}")
        return json.dumps([
            {"currency": "USD", "rate": 82.45},
            {"currency": "EUR", "rate": 94.20}
        ])


def get_stock_prices() -> str:
    """Возвращает текущие цены акций."""
    try:
        import yfinance as yf
        
        # Список тикеров для отслеживания
        tickers = ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
        prices = []
        
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                # Получаем последнюю цену закрытия
                last_price = stock.history(period="1d")['Close'].iloc[-1]
                prices.append({
                    "stock": ticker,
                    "price": round(float(last_price), 2)
                })
            except Exception as e:
                logging.error(f"Ошибка при получении данных для {ticker}: {str(e)}")
                continue
        
        if not prices:  # Если не удалось получить ни одной цены
            return json.dumps([
                {"stock": "AAPL", "price": 208.37},
                {"stock": "AMZN", "price": 186.54},
                {"stock": "GOOGL", "price": 159.28},
                {"stock": "MSFT", "price": 387.30},
                {"stock": "TSLA", "price": 259.51}
            ])
        
        return json.dumps(prices)
    except ImportError:
        logging.error("Библиотека yfinance не установлена")
        return json.dumps([
            {"stock": "AAPL", "price": 208.37},
            {"stock": "AMZN", "price": 186.54},
            {"stock": "GOOGL", "price": 159.28},
            {"stock": "MSFT", "price": 387.30},
            {"stock": "TSLA", "price": 259.51}
        ])


def summarize_expenses(df, start_date, end_date):
    """Суммирование расходов по категориям."""
    filtered = df[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date) & (df["Сумма операции"] < 0)]
    grouped = filtered.groupby("Категория")["Сумма операции"].sum().reset_index()
    grouped["Сумма операции"] = abs(grouped["Сумма операции"])
    main_categories = grouped.nlargest(7, "Сумма операции").to_dict("records")
    other_amount = grouped[~grouped["Категория"].isin([cat["Категория"] for cat in main_categories])]["Сумма операции"].sum()
    if other_amount > 0:
        main_categories.append({"Категория": "Остальное", "Сумма операции": round(other_amount, 2)})
    transfers_and_cash = filtered[filtered["Категория"].isin(["Наличные", "Переводы"])].groupby("Категория")["Сумма операции"].sum().reset_index()
    transfers_and_cash["Сумма операции"] = -transfers_and_cash["Сумма операции"]
    transfers_and_cash = transfers_and_cash.to_dict("records")
    total_expenses = round(abs(filtered["Сумма операции"].sum()), 2)
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
