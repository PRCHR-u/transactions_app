import json
import logging
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd
import re

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def profitable_categories(data: pd.DataFrame, year: int, month: int) -> dict:
    try:
        data["Дата операции"] = pd.to_datetime(data["Дата операции"])
        data["Категория"] = data["Категория"].astype(str)  # Преобразуем категории в строки

        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - pd.Timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - pd.Timedelta(days=1)

        filtered_data = data[
            (data["Дата операции"] >= start_date) &
            (data["Дата операции"] <= end_date)
        ]

        if "Сумма операции" in filtered_data.columns:
            filtered_data["Абсолютный кешбэк"] = (
                filtered_data["Кешбэк"].abs() * filtered_data["Сумма операции"].abs() / 100
            )
        else:
            filtered_data["Абсолютный кешбэк"] = filtered_data["Кешбэк"].abs()

        grouped = filtered_data.groupby("Категория")["Абсолютный кешбэк"].sum().reset_index()
        result = {row["Категория"]: round(row["Абсолютный кешбэк"], 2) for _, row in grouped.iterrows()}

        expected_categories = [
            "Супермаркеты", "Переводы", "Различные товары",
            "Бонусы", "Кэшбэк", "Пополнение_BANK007", "Проценты_на_остаток"
        ]
        for category in expected_categories:
            if category not in result:
                result[category] = 0.0

        return result
    except Exception as e:
        logging.error(f"Ошибка при анализе выгодных категорий: {e}")
        return {}


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    try:
        year, month_num = map(int, month.split("-"))
        start_date = datetime(year, month_num, 1)
        if month_num == 12:
            end_date = datetime(year + 1, 1, 1) - pd.Timedelta(days=1)
        else:
            end_date = datetime(year, month_num + 1, 1) - pd.Timedelta(days=1)

        # Преобразуем транзакции в DataFrame для удобства
        df = pd.DataFrame(transactions)
        df["Дата операции"] = pd.to_datetime(df["Дата операции"])

        # Фильтруем транзакции по указанному месяцу
        filtered_transactions = df[
            (df["Дата операции"] >= start_date) &
            (df["Дата операции"] <= end_date)
        ]

        # Рассчитываем сумму для инвестиций
        total_invested = 0
        for _, tx in filtered_transactions.iterrows():
            amount = abs(tx["Сумма операции"])  # Работаем с модулем суммы
            if amount % limit != 0:
                total_invested += limit - (amount % limit)

        return round(total_invested, 2)
    except Exception as e:
        logging.error(f"Ошибка при расчете инвестиций: {e}")
        return 0.0


def simple_search(query: str, transactions: pd.DataFrame) -> List[Dict[str, Any]]:
    try:
        query_lower = query.lower()
        # Фильтруем DataFrame по категории
        result = transactions[
            transactions["Категория"].str.lower().str.contains(query_lower)
        ]
        # Преобразуем результат в список словарей
        return result.to_dict("records")
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


def search_physical_transfers(transactions: pd.DataFrame) -> List[Dict[str, Any]]:
    try:
        # Фильтруем транзакции по категории "Переводы"
        result = transactions[transactions["Категория"] == "Переводы"]

        # Преобразуем "Дата операции" в строку и удаляем "Номер карты"
        result = result.drop(columns=["Номер карты"])  # Удаляем ненужную колонку
        result["Дата операции"] = result["Дата операции"].dt.strftime("%Y-%m-%d")  # Преобразуем дату в строку

        # Преобразуем результат в список словарей
        return result.to_dict("records")
    except Exception as e:
        logging.error(f"Ошибка при поиске переводов: {e}")
        return []
