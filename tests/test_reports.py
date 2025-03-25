import pytest
import pandas as pd
from src.reports import (
    spending_by_category,
    spending_by_weekday,
    spending_by_workday
)


def test_spending_by_category(sample_transactions):
    result = spending_by_category(sample_transactions, "Супермаркеты", date="2023-10-15")
    assert result == {"category": "Супермаркеты", "total": 2524.0}

def test_spending_by_weekday(sample_transactions):
    result = spending_by_weekday(sample_transactions, date="2023-10-15")
    assert result == {
        "Monday": 0.0,
        "Tuesday": 0.0,
        "Wednesday": 0.0,
        "Thursday": 0.0,
        "Friday": 2524.0,
        "Saturday": 0.0,
        "Sunday": 0.0
    }

def test_spending_by_workday(sample_transactions):
    result = spending_by_workday(sample_transactions, date="2023-10-15")
    assert result == {
        "Рабочий день": 2524.0,
        "Выходной день": 0.0
    }
