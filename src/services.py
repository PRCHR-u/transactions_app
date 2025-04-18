import json
import logging
import re

import numpy as np
import pandas as pd


def profitable_categories(
    df, year, month):
    """Расчет расходов по категориям за указанный месяц."""
    df["Дата операции"] = pd.to_datetime(
        df["Дата операции"])
    mask = (
        (df["Дата операции"].dt.year == year) & (df["Дата операции"].dt.month == month)
    )
    filtered_df = df[mask].copy()
    filtered_df = filtered_df[filtered_df["Сумма операции"] < 0]  # Только расходы
    filtered_df["Сумма операции"] = filtered_df["Сумма операции"].abs()

    # Группируем по категориям и суммируем расходы
    category_totals = filtered_df.groupby("Категория")["Сумма операции"].sum()

    all_categories = [
        "Супермаркеты",
        "Переводы",
        "Различные товары",
        "Бонусы",
        "Пополнение_BANK007",
        "Проценты_на_остаток",
        "Кэшбэк",
    ]

    # Формируем словарь с суммами по категориям
    result = {
        cat: float(category_totals.get(cat, 0.0)) for cat in all_categories
    }
    return json.dumps(result, ensure_ascii=False)


def investment_bank(month, transactions, threshold):
    """Расчет суммы для округления трат в Инвесткопилку за указанный месяц."""
    df = pd.DataFrame(transactions)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"])
    mask = df["Дата операции"].dt.strftime("%Y-%m") == month
    filtered_df = df[mask & (df["Сумма операции"] < 0)].copy()

    if filtered_df.empty:
        return json.dumps(0.0)

    total_amount = abs(filtered_df["Сумма операции"].sum())
    rounded_amount = np.ceil(total_amount / threshold) * threshold
    investment_amount = rounded_amount - total_amount
    return json.dumps(round(float(investment_amount), 2))


def simple_search(query, transactions):
    query = query.lower()
    matches = [
        t
        for t in transactions
        if query in t["Категория"].lower() or query in t["Описание"].lower()
    ]
    return json.dumps(matches, ensure_ascii=False)


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def search_phone_numbers(transactions):
    logging.info("Вызвана функция search_phone_numbers")  # type: ignore
    try:
        phone_pattern = r"\+7\s+\d{3}\s+\d{2,3}[-\s]\d{2}[-\s]\d{2}"  # noqa: E501
        matches = [
            t for t in transactions if re.search(phone_pattern, t["Описание"])
        ]
        return json.dumps(matches, ensure_ascii=False)  # type: ignore
    except Exception as e:
        logging.error(f"Ошибка в функции search_phone_numbers: {e}")
        return json.dumps([], ensure_ascii=False)


def search_physical_transfers(transactions):
    exclude_pattern = re.compile(r"карт|счет|кредитн|перевод|тп", re.IGNORECASE)
    name_pattern = re.compile(
        r"^[А-ЯA-Z][а-яa-z]+(?:\s+[А-ЯA-Z]\.?)?$|^[А-ЯA-Z][а-яa-z]+\s+[А-ЯA-Z][а-яa-z]+$"  # noqa: E501
    )
    matches = [
        t
        for t in transactions
        if t["Категория"] == "Переводы"
        and not exclude_pattern.search(t["Описание"].lower())
        and name_pattern.match(t["Описание"])
    ]
    return json.dumps(matches, ensure_ascii=False)
