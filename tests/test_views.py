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
def test_events_view(mock_read_transactions, mock_get_currency_rates, mock_get_stock_prices):
    # Создаем мок-данные
    sample_transactions = pd.DataFrame({
        "Дата операции": ["2023-10-01", "2023-10-10"],
        "Сумма операции": [-1262.00, -7.94],
        "Категория": ["Супермаркеты", "Супермаркеты"]
    })
    mock_read_transactions.return_value = sample_transactions
    mock_get_currency_rates.return_value = [{"currency": "USD", "rate": 0.0136}, {"currency": "EUR", "rate": 0.0115}]
    mock_get_stock_prices.return_value = [{"stock": "AAPL", "price": 150.12}, {"stock": "AMZN", "price": 3173.18}]

    # Вызываем функцию
    response = events_view("2023-10-15 14:30:00", mock_read_transactions, mock_get_currency_rates, mock_get_stock_prices)

    # Проверяем результат
    assert isinstance(response, dict), "Функция events_view должна возвращать словарь"
    assert "expenses" in response, "Ключ 'expenses' отсутствует в ответе"
    assert "total_amount" in response["expenses"], "Ключ 'total_amount' отсутствует в 'expenses'"
    assert response["expenses"]["total_amount"] == -1269.94
