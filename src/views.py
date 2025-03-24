import json

from _pytest import logging

from src.utils import (
    read_transactions,
    get_date_range,
    get_greeting,
    get_card_summaries,
    get_top_transactions,
    get_currency_rates,
    get_stock_prices,
    summarize_expenses,
    summarize_income
)


def home_view(input_date_str):
    """
    Функция для страницы «Главная».

    Принимает на вход строку с датой и временем в формате YYYY-MM-DD HH:MM:SS.
    Возвращает JSON-ответ с данными о транзакциях, курсах валют и ценах на акции.
    """
    df = read_transactions()
    if df.empty:
        logging.error("Нет данных для анализа.")
        return {}

    start, end = get_date_range(input_date_str)
    greeting = get_greeting(end.hour)

    # Загрузка пользовательских настроек
    try:
        with open("user_settings.json") as f:
            settings = json.load(f)
        currencies = settings.get("user_currencies", [])
        stocks = settings.get("user_stocks", [])
    except Exception as e:
        logging.error(f"Ошибка чтения пользовательских настроек: {e}")
        currencies = []
        stocks = []

    # Получение данных для JSON-ответа
    response = {
        "greeting": greeting,
        "cards": get_card_summaries(df, start, end),
        "top_transactions": get_top_transactions(df, start, end),
        "currency_rates": get_currency_rates(currencies),
        "stock_prices": get_stock_prices(stocks)
    }
    return response


def events_view(input_date_str, period="M"):
    """
    Функция для страницы «События».

    Принимает на вход строку с датой и временем в формате YYYY-MM-DD HH:MM:SS.
    Второй необязательный параметр period определяет диапазон данных (W, M, Y, ALL).
    Возвращает JSON-ответ с данными о расходах, поступлениях, курсах валют и ценах на акции.
    """
    df = read_transactions()
    if df.empty:
        logging.error("Нет данных для анализа.")
        return {}

    start, end = get_date_range(input_date_str, period)

    # Загрузка пользовательских настроек
    try:
        with open("user_settings.json") as f:
            settings = json.load(f)
        currencies = settings.get("user_currencies", [])
        stocks = settings.get("user_stocks", [])
    except Exception as e:
        logging.error(f"Ошибка чтения пользовательских настроек: {e}")
        currencies = []
        stocks = []

    # Получение данных для JSON-ответа
    response = {
        "expenses": summarize_expenses(df, start, end),
        "income": summarize_income(df, start, end),
        "currency_rates": get_currency_rates(currencies),
        "stock_prices": get_stock_prices(stocks)
    }
    return response
