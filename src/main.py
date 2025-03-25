import json

from reports import spending_by_category, spending_by_weekday, spending_by_workday
from src.services import (
    investment_bank,
    profitable_categories,
    search_phone_numbers,
    search_physical_transfers,
    simple_search,
)
from utils import read_transactions
from views import events_view, home_view


def main():
    input_date_str = "2023-10-15 14:30:00"  # Пример даты

    # Главная страница
    home_response = home_view(input_date_str)
    print("Главная страница:")
    print(json.dumps(home_response, ensure_ascii=False, indent=4))

    # Страница События
    events_response = events_view(input_date_str, period="M")
    print("\nСтраница События:")
    print(json.dumps(events_response, ensure_ascii=False, indent=4))

    # Пример использования сервисов
    df = read_transactions()
    transactions = df.to_dict("records")

    # Выгодные категории повышенного кешбэка
    profitable_cats = profitable_categories(df, 2023, 10)
    print("\nВыгодные категории повышенного кешбэка:")
    print(json.dumps(profitable_cats, ensure_ascii=False, indent=4))

    # Инвесткопилка
    invest_bank_result = investment_bank("2023-10", transactions, 50)
    print("\nИнвесткопилка:")
    print(invest_bank_result)

    # Простой поиск
    search_result = simple_search("Супермаркеты", transactions)
    print("\nПростой поиск:")
    print(json.dumps(search_result, ensure_ascii=False, indent=4))

    # Поиск по телефонным номерам
    phone_search_result = search_phone_numbers(transactions)
    print("\nПоиск по телефонным номерам:")
    print(json.dumps(phone_search_result, ensure_ascii=False, indent=4))

    # Поиск переводов физическим лицам
    physical_transfer_search_result = search_physical_transfers(transactions)
    print("\nПоиск переводов физическим лицам:")
    print(json.dumps(physical_transfer_search_result, ensure_ascii=False, indent=4))

    # Отчеты
    category_report = spending_by_category(df, "Супермаркеты", date="2023-10-15")
    print("\nОтчет по категории Супермаркеты:")
    print(json.dumps(category_report, ensure_ascii=False, indent=4))

    weekday_report = spending_by_weekday(df, date="2023-10-15")
    print("\nОтчет по дням недели:")
    print(json.dumps(weekday_report, ensure_ascii=False, indent=4))

    workday_report = spending_by_workday(df, date="2023-10-15")
    print("\nОтчет по рабочим и выходным дням:")
    print(json.dumps(workday_report, ensure_ascii=False, indent=4))


if __name__ == "__main__":
    main()
