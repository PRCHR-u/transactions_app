import pandas as pd
import pytest
from unittest.mock import patch
from src.views import events_view

@pytest.fixture
def sample_transactions():
    data = [
        {"Дата операции": "2023-10-01", "Сумма операции": -1262.00, "Категория": "Супермаркеты"},
        {"Дата операции": "2023-10-10", "Сумма операции": -7.94, "Категория": "Супермаркеты"},
    ]
    return pd.DataFrame(data)

@patch("src.utils.get_stock_prices")
@patch("src.utils.get_currency_rates")
@patch("src.utils.read_transactions")
def test_events_view(mock_read_transactions, mock_get_currency_rates, mock_get_stock_prices, sample_transactions):
    mock_read_transactions.return_value = sample_transactions
    mock_get_currency_rates.return_value = [{"currency": "USD", "rate": 0.0136}, {"currency": "EUR", "rate": 0.0115}]
    mock_get_stock_prices.return_value = [{"stock": "AAPL", "price": 150.12}, {"stock": "AMZN", "price": 3173.18}]
    response = events_view("2023-10-15 14:30:00")
    assert response["expenses"]["total_amount"] == -1269.94  # Отрицательное значение, так как это расходы
    assert response["income"]["total_amount"] == 0.0
    assert len(response["expenses"]["main"]) == 1
    assert response["expenses"]["main"][0]["Категория"] == "Супермаркеты"
    assert response["expenses"]["main"][0]["amount"] == -1269.94
    assert len(response["income"]["main"]) == 0
    assert response["currency_rates"] == [{"currency": "USD", "rate": 0.0136}, {"currency": "EUR", "rate": 0.0115}]
    assert response["stock_prices"] == [{"stock": "AAPL", "price": 150.12}, {"stock": "AMZN", "price": 3173.18}]
