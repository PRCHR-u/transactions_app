import json
import logging
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd
import re

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def profitable_categories(data: pd.DataFrame, year: int, month: int) -> Dict[str, float]:
    """
    Функция для анализа выгодности категорий повышенного кешбэка.

    На вход принимает данные с транзакциями, год и месяц.
    На выходе возвращает JSON с анализом, сколько на каждой категории можно заработать кешбэка.

    :param data: Датафрейм с транзакциями.
    :param year: Год для анализа.
    :param month: Месяц для анализа.
    :return: JSON с анализом кешбэка по категориям.
    """
    try:
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - pd.Timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - pd.Timedelta(days=1)

        filtered_data = data[
            (data["Дата операции"] >= start_date) &
            (data["Дата операции"] <= end_date)
            ]

        grouped = filtered_data.groupby("Категория")["Кешбэк"].sum().reset_index()
        result = {row["Категория"]: round(row["Кешбэк"], 2) for _, row in grouped.iterrows()}
        return result
    except Exception as e:
        logging.error(f"Ошибка при анализе выгодных категорий: {e}")
        return {}


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """
    Функция для расчета суммы, которую можно отложить в «Инвесткопилку».

    :param month: Месяц для которого рассчитывается отложенная сумма (формат 'YYYY-MM').
    :param transactions: Список словарей с транзакциями.
    :param limit: Предел, до которого нужно округлять суммы операций.
    :return: Сумма, которую удалось бы отложить в «Инвесткопилку».
    """
    try:
        year, month_num = map(int, month.split("-"))
        start_date = datetime(year, month_num, 1)
        if month_num == 12:
            end_date = datetime(year + 1, 1, 1) - pd.Timedelta(days=1)
        else:
            end_date = datetime(year, month_num + 1, 1) - pd.Timedelta(days=1)

        filtered_transactions = [
            tx for tx in transactions
            if start_date <= datetime.strptime(tx["Дата операции"], "%Y-%m-%d") <= end_date
        ]

        total_invested = sum(
            (tx["Сумма операции"] + limit - 1) // limit * limit - tx["Сумма операции"]
            for tx in filtered_transactions
        )
        return round(total_invested, 2)
    except Exception as e:
        logging.error(f"Ошибка при расчете инвестиций: {e}")
        return 0.0


def simple_search(query: str, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Функция для простого поиска транзакций по описанию или категории.

    :param query: Строка для поиска.
    :param transactions: Список словарей с транзакциями.
    :return: Список транзакций, содержащих запрос в описании или категории.
    """
    try:
        query_lower = query.lower()
        result = [
            tx for tx in transactions
            if query_lower in tx["Описание"].lower() or query_lower in tx["Категория"].lower()
        ]
        return result
    except Exception as e:
        logging.error(f"Ошибка при простом поиске: {e}")
        return []


def search_phone_numbers(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Функция для поиска транзакций, содержащих мобильные номера.

    :param transactions: Список словарей с транзакциями.
    :return: Список транзакций, содержащих мобильные номера.
    """
    try:
        phone_pattern = re.compile(r'\+7\s?\d{3}[-\s]?\d{2}[-\s]?\d{2}[-\s]?\d{2}')
        result = [
            tx for tx in transactions
            if phone_pattern.search(tx["Описание"])
        ]
        return result
    except Exception as e:
        logging.error(f"Ошибка при поиске телефонных номеров: {e}")
        return []


def search_physical_transfers(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Функция для поиска транзакций, относящихся к переводам физическим лицам.

    :param transactions: Список словарей с транзакциями.
    :return: Список транзакций, относящихся к переводам физическим лицам.
    """
    try:
        transfer_pattern = re.compile(r'[А-Яа-яЁё]\.\s?[А-Яа-яЁё]+')
        result = [
            tx for tx in transactions
            if tx["Категория"] == "Переводы" and transfer_pattern.search(tx["Описание"])
        ]
        return result
    except Exception as e:
        logging.error(f"Ошибка при поиске переводов физическим лицам: {e}")
        return []
