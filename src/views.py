from src.utils import (
    read_transactions,
    get_date_range,
    get_greeting,
    get_card_summaries,
    get_top_transactions,
    get_currency_rates,
    get_stock_prices
)

def home_view(current_time):
    """
    Возвращает данные для главной страницы.
    """
    greeting = get_greeting(current_time)
    transactions = read_transactions("path_to_transactions.csv")
    cards = get_card_summaries(transactions)
    top_transactions = get_top_transactions(transactions)
    currency_rates = get_currency_rates()
    stock_prices = get_stock_prices()

    return {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }

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
    stock_prices = get_stock_prices()

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
    # Ensure the "Сумма операции" column exists
    if "Сумма операции" not in transactions.columns:
        raise ValueError("Столбец 'Сумма операции' отсутствует в данных.")

    # Filter for expenses (negative amounts)
    expenses = transactions[transactions["Сумма операции"] < 0]

    # Calculate total expenses
    total_amount = expenses["Сумма операции"].sum()

    # Group by category
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
    income = transactions[transactions["Сумма операции"] > 0]
    total_amount = income["Сумма операции"].sum()
    main_categories = income.groupby("Категория")["Сумма операции"].sum().reset_index()
    main_categories = main_categories.rename(columns={"Сумма операции": "amount"})
    main_categories = main_categories.to_dict("records")
    return {"total_amount": total_amount, "main": main_categories}
