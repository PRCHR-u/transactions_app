from src.utils import (
    read_transactions,
    get_currency_rates,
    get_stock_prices
)

def events_view(current_time):
    """
    Возвращает данные для страницы событий.
    """
    # Read transactions (use a valid file path or mock it in tests)
    transactions = read_transactions("data/transactions.csv")

    # Calculate expenses and income
    expenses = calculate_expenses(transactions)
    income = calculate_income(transactions)

    # Get currency rates and stock prices
    currency_rates = get_currency_rates(currencies=["USD", "EUR"])
    stock_prices = get_stock_prices(stocks=["AAPL", "AMZN"])

    return {
        "expenses": expenses,
        "income": income,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }

def calculate_expenses(transactions):
    """
    Рассчитывает расходы.
    """
    if transactions.empty:
        return {"total_amount": 0, "main": []}

    if "Сумма операции" not in transactions.columns:
        raise ValueError("Столбец 'Сумма операции' отсутствует в данных.")

    expenses = transactions[transactions["Сумма операции"] < 0]
    total_amount = expenses["Сумма операции"].sum()
    main_categories = expenses.groupby("Категория")["Сумма операции"].sum().reset_index()
    main_categories = main_categories.rename(columns={"Сумма операции": "amount"})
    main_categories = main_categories.to_dict("records")

    return {
        "total_amount": total_amount,
        "main": main_categories
    }

def calculate_income(transactions):
    """
    Рассчитывает доходы.
    """
    if transactions.empty:
        return {"total_amount": 0, "main": []}

    if "Сумма операции" not in transactions.columns:
        raise ValueError("Столбец 'Сумма операции' отсутствует в данных.")

    income = transactions[transactions["Сумма операции"] > 0]
    total_amount = income["Сумма операции"].sum()
    main_categories = income.groupby("Категория")["Сумма операции"].sum().reset_index()
    main_categories = main_categories.rename(columns={"Сумма операции": "amount"})
    main_categories = main_categories.to_dict("records")
    return {"total_amount": total_amount, "main": main_categories}
