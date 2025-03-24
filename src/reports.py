import json
import logging
from datetime import datetime, timedelta
import pandas as pd
from typing import Optional, Callable, Any

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def save_report(filename: Optional[str] = None):
    """
    Декоратор для сохранения отчета в файл.

    :param filename: Имя файла для сохранения отчета. Если None, используется имя по умолчанию.
    """

    def decorator(func: Callable[..., Any]):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if filename:
                with open(filename, "w") as f:
                    json.dump(result, f, ensure_ascii=False, indent=4)
            else:
                default_filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(default_filename, "w") as f:
                    json.dump(result, f, ensure_ascii=False, indent=4)
            return result

        return wrapper

    return decorator


@save_report()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> dict:
    """
    Функция для получения трат по заданной категории за последние три месяца.

    :param transactions: Датафрейм с транзакциями.
    :param category: Название категории.
    :param date: Опциональная дата для отсчета трехмесячного периода (строка в формате 'YYYY-MM-DD').
    :return: JSON с тратами по категории.
    """
    try:
        if date is None:
            date = datetime.now()
        else:
            date = datetime.strptime(date, "%Y-%m-%d")

        three_months_ago = date - pd.DateOffset(months=3)
        filtered = transactions[
            (transactions["Дата операции"] >= three_months_ago) &
            (transactions["Дата операции"] <= date) &
            (transactions["Категория"] == category)
            ]
        total = filtered["Сумма операции"].sum()
        return {"category": category, "total": round(-total, 2)}
    except Exception as e:
        logging.error(f"Ошибка при формировании отчета по категории: {e}")
        return {}


@save_report()
def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> dict:
    """
    Функция для получения средних трат по дням недели за последние три месяца.

    :param transactions: Датафрейм с транзакциями.
    :param date: Опциональная дата для отсчета трехмесячного периода (строка в формате 'YYYY-MM-DD').
    :return: JSON со средними тратами по дням недели.
    """
    try:
        if date is None:
            date = datetime.now()
        else:
            date = datetime.strptime(date, "%Y-%m-%d")

        three_months_ago = date - pd.DateOffset(months=3)
        filtered = transactions[
            (transactions["Дата операции"] >= three_months_ago) &
            (transactions["Дата операции"] <= date)
            ]
        filtered["День недели"] = filtered["Дата операции"].dt.day_name()
        grouped = filtered.groupby("День недели")["Сумма операции"].mean().reset_index()
        result = {row["День недели"]: round(-row["Сумма операции"], 2) for _, row in grouped.iterrows()}
        return result
    except Exception as e:
        logging.error(f"Ошибка при формировании отчета по дням недели: {e}")
        return {}


@save_report()
def spending_by_workday(transactions: pd.DataFrame, date: Optional[str] = None) -> dict:
    """
    Функция для получения средних трат в рабочий и выходной день за последние три месяца.

    :param transactions: Датафрейм с транзакциями.
    :param date: Опциональная дата для отсчета трехмесячного периода (строка в формате 'YYYY-MM-DD').
    :return: JSON со средними тратами в рабочий и выходной день.
    """
    try:
        if date is None:
            date = datetime.now()
        else:
            date = datetime.strptime(date, "%Y-%m-%d")

        three_months_ago = date - pd.DateOffset(months=3)
        filtered = transactions[
            (transactions["Дата операции"] >= three_months_ago) &
            (transactions["Дата операции"] <= date)
            ]
        filtered["Рабочий день"] = filtered["Дата операции"].dt.weekday < 5
        grouped = filtered.groupby("Рабочий день")["Сумма операции"].mean().reset_index()
        result = {}
        for _, row in grouped.iterrows():
            if row["Рабочий день"]:
                result["Рабочий день"] = round(-row["Сумма операции"], 2)
            else:
                result["Выходной день"] = round(-row["Сумма операции"], 2)
        return result
    except Exception as e:
        logging.error(f"Ошибка при формировании отчета по рабочим и выходным дням: {e}")
        return {}
