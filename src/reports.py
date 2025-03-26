import json
import logging
from datetime import datetime
from typing import Optional

import pandas as pd

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> dict:
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
        # Убедимся, что суммируем только отрицательные значения
        total = filtered[filtered["Сумма операции"] < 0]["Сумма операции"].sum()
        return {"category": category, "total": round(-total, 2)}
    except Exception as e:
        logging.error(f"Ошибка при формировании отчета по категории: {e}")
        return {}


def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> dict:
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
        filtered["День недели"] = filtered["Дата операции"].dt.day_name(locale="ru_RU")
        # Убедимся, что учитываем только отрицательные значения
        filtered = filtered[filtered["Сумма операции"] < 0]
        grouped = filtered.groupby("День недели")["Сумма операции"].mean().reset_index()
        result = {row["День недели"]: round(-row["Сумма операции"], 2) for _, row in grouped.iterrows()}
        return result
    except Exception as e:
        logging.error(f"Ошибка при формировании отчета по дням недели: {e}")
        return {}


def spending_by_workday(transactions: pd.DataFrame, date: Optional[str] = None) -> dict:
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
        # Убедимся, что учитываем только отрицательные значения
        filtered = filtered[filtered["Сумма операции"] < 0]
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
