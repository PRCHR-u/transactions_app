import logging

import pandas as pd
import pytest
from src.services import (
    profitable_categories,
    investment_bank,
    simple_search,
    search_phone_numbers,
    search_physical_transfers
)


def test_profitable_categories(sample_transactions):
    # Преобразуем данные в DataFrame
    df = pd.DataFrame(sample_transactions)

    # Преобразуем колонку "Дата операции" в datetime, если это еще не сделано
    df["Дата операции"] = pd.to_datetime(df["Дата операции"])

    # Проверяем, что данные содержат транзакции за октябрь 2023 года
    start_date = pd.Timestamp("2023-10-01")
    end_date = pd.Timestamp("2023-10-31")
    october_transactions = df[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)]

    # Убедимся, что есть хотя бы одна транзакция за октябрь
    assert len(october_transactions) > 0


def test_investment_bank(sample_transactions):
    result = investment_bank("2023-10", sample_transactions, 50)
    assert result == 131.83  # Ожидаемое значение на основе предоставленных данных


logging.basicConfig(level=logging.INFO)


def test_simple_search(sample_transactions):
    # Выведем данные для проверки
    for tx in sample_transactions:
        logging.info(f"Транзакция: {tx}")

    result = simple_search("Супермаркеты", sample_transactions)
    assert len(result) == 3  # Проверяем, что найдено 3 транзакции


def test_search_phone_numbers(sample_transactions):
    result = search_phone_numbers(sample_transactions)
    assert result == []

def test_search_physical_transfers(sample_transactions):
    result = search_physical_transfers(sample_transactions)
    assert result == [
        {
            "Дата операции": "2023-10-15",
            "Сумма операции": -1198.23,
            "Кешбэк": 11.98,
            "Категория": "Переводы",
            "Описание": "Перевод Кредитная карта. ТП 10.2 RUR"
        },
        {
            "Дата операции": "2023-08-25",
            "Сумма операции": 1000.00,
            "Кешбэк": 10.00,
            "Категория": "Переводы",
            "Описание": "Валерий А."
        }
    ]
