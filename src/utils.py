import pandas as pd
from datetime import datetime, timedelta
import requests
import json
import logging
import os
from dotenv import load_dotenv

load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_transactions(file_path="data/operations.xls"):
    """Чтение транзакций из файла."""
    try:
        # Проверка расширения файла
        if file_path.endswith('.xlsx'):
            engine = 'openpyxl'
        elif file_path.endswith('.xls'):
            engine = 'xlrd'
        elif file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        else:
            raise ValueError("Неподдерживаемый формат файла. Используйте .xls, .xlsx или .csv.")

        df = pd.read_excel(file_path, engine=engine)
        df['Дата операции'] = pd.to_datetime(df['Дата операции'])
        df['Дата платежа'] = pd.to_datetime(df['Дата платежа'])

        # Проверка обязательных столбцов
        required_columns = ["Сумма операции", "Категория", "Дата операции"]
        for column in required_columns:
            if column not in df.columns:
                logging.warning(f"Столбец '{column}' отсутствует в данных.")
                return pd.DataFrame()

        return df
    except Exception as e:
        logging.error(f"Ошибка чтения файла: {e}")
        return pd.DataFrame()


def mock_read_transactions(file_path):
        return pd.DataFrame([
            {"Дата операции": "2023-10-01", "Сумма операции": -1262.00, "Категория": "Супермаркеты"},
            {"Дата операции": "2023-10-10", "Сумма операции": -7.94, "Категория": "Супермаркеты"},
        ])


def get_date_range(date_str):
    """
    Возвращает диапазон дат для заданной даты.

    Args:
        date_str (str): Дата в формате "YYYY-MM-DD HH:MM:SS".

    Returns:
        tuple: (start_date, end_date), где start_date и end_date — объекты datetime.
    """
    date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    start_date = date - timedelta(days=14)  # Начало диапазона (14 дней назад)
    end_date = date + timedelta(days=10)    # Конец диапазона (10 дней вперед)
    return start_date, end_date


def get_greeting(hour):
    """Получение приветствия в зависимости от часа."""
    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_card_summaries(transactions, start_date, end_date):
    """
    Возвращает сводку по картам за заданный диапазон дат.

    Args:
        transactions (pd.DataFrame): DataFrame с транзакциями.
        start_date (datetime): Начальная дата диапазона.
        end_date (datetime): Конечная дата диапазона.

    Returns:
        list: Список словарей с информацией по каждой карте.
    """
    # Фильтрация по дате
    filtered = transactions[
        (transactions["Дата операции"] >= start_date) &
        (transactions["Дата операции"] <= end_date)
        ]

    # Отладочный вывод
    print("Отфильтрованные транзакции:")
    print(filtered)

    # Группировка по последним цифрам карты
    grouped = filtered.groupby("Номер карты")

    # Формирование результата
    summaries = []
    for last_digits, group in grouped:
        total_spent = group["Сумма операции"].sum()  # Общая сумма потраченных средств
        cashback = group["Кешбэк"].sum()  # Общий кешбэк
        summaries.append({
            "last_digits": last_digits[-4:],  # Последние 4 цифры номера карты
            "total_spent": float(round(total_spent, 2)),  # Преобразуем в стандартный float
            "cashback": float(round(cashback, 2))  # Преобразуем в стандартный float
        })

    # Сортировка по total_spent (по убыванию)
    summaries.sort(key=lambda x: x["total_spent"], reverse=True)

    return summaries


def get_top_transactions(transactions, start_date, end_date):
    """
    Возвращает транзакции в заданном диапазоне дат, отсортированные по сумме.

    Args:
        transactions (pd.DataFrame): DataFrame с транзакциями.
        start_date (datetime): Начальная дата диапазона.
        end_date (datetime): Конечная дата диапазона.

    Returns:
        list: Список словарей с информацией о транзакциях.
    """
    # Фильтрация по дате
    filtered = transactions[
        (transactions["Дата операции"] >= start_date) &
        (transactions["Дата операции"] <= end_date)
        ]

    # Сортировка по сумме (по убыванию)
    sorted_transactions = filtered.sort_values(by="Сумма операции", ascending=False)

    # Форматирование результата
    result = [
        {
            "date": row["Дата операции"].strftime("%d.%m.%Y"),
            "amount": row["Сумма операции"],
            "category": row["Категория"],
            "description": row["Описание"]
        }
        for _, row in sorted_transactions.iterrows()
    ]

    return result


def get_currency_rates(currencies=["USD", "EUR"], fetch_data=None):
    """
    Получение курсов валют из внешнего API или с использованием предоставленной функции.

    Args:
        currencies (list, optional): Список валют для получения курсов. Defaults to ["USD", "EUR"].
        fetch_data (callable, optional): Функция для получения данных о курсах валют.
                                        Если предоставлена, используется для получения данных. Defaults to None.

    Returns:
        list: Список словарей, где каждый словарь содержит информацию о валюте и ее курсе по отношению к RUB.
              Пример: [{'currency': 'USD', 'rate': 84.7458}, {'currency': 'EUR', 'rate': 91.7431}]
              Возвращает пустой список в случае ошибки.
    """

    if fetch_data:
        try:
            return fetch_data(currencies)
        except Exception as e:
            logging.error(f"Ошибка при использовании fetch_data: {e}")
            return []

    api_key = os.getenv("CURRENCY_API_KEY")
    base_url = "https://www.alphavantage.co/documentation/"  # Базовый URL для запроса к API

    try:
        response = requests.get(base_url, timeout=10)  # Отправка GET-запроса к API
        response.raise_for_status()  # Вызов исключения для HTTP-ошибок
        rates = response.json()["rates"]  # Извлечение курсов валют из JSON-ответа
        currency_rates = [  # Формирование списка курсов валют на основе полученных данных
            {"currency": c, "rate": round(1 / rates[c], 4)}
            for c in currencies  # Перебор запрошенных валют
            if c in rates  # Проверка наличия валюты в полученных данных
        ]
        return currency_rates  # Возврат списка курсов валют

    except requests.RequestException as e:
        logging.error(f"Ошибка HTTP запроса при получении курсов валют: {e}")
        return []
    except (KeyError, ValueError) as e:
        logging.error(f"Ошибка обработки ответа API: {e}")
        return []
    except Exception as e:  # Обработка любых других исключений
        logging.error(f"Неизвестная ошибка при получении курсов валют: {e}")
        return []


def get_stock_prices(stocks, fetch_data=None):
    """
    Возвращает цены акций для указанных тикеров.

    Args:
        stocks (list): Список тикеров акций (например, ["AAPL", "TSLA"]).
        fetch_data (callable): Функция для получения данных (опционально, для тестов).

    Returns:
        list: Список словарей с информацией о ценах акций.
    """
    if fetch_data:
        return fetch_data(stocks)

    # Реальный вызов API по умолчанию
    results = []
    for stock in stocks:
        try:
            # Пример реального API-вызова (замените на ваш эндпоинт)
            response = requests.get(
                f"https://www.alphavantage.co/documentation/{stock}",
                timeout=5
            )
            response.raise_for_status()
            results.append({
                "stock": stock,
                "price": response.json()['price']
            })
        except (requests.RequestException, KeyError):
            results.append({"stock": stock, "price": 0.0})

    return results


def summarize_expenses(df, start_date, end_date):
    """Суммирование расходов по категориям."""
    filtered = df[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date) & (df["Сумма операции"] < 0)]
    grouped = filtered.groupby("Категория")["Сумма операции"].sum().reset_index()
    grouped["Сумма операции"] = -grouped["Сумма операции"]
    main_categories = grouped.nlargest(7, "Сумма операции").to_dict("records")
    other_amount = grouped[~grouped["Категория"].isin([cat["Категория"] for cat in main_categories])]["Сумма операции"].sum()
    if other_amount > 0:
        main_categories.append({"Категория": "Остальное", "Сумма операции": round(other_amount, 2)})
    transfers_and_cash = filtered[filtered["Категория"].isin(["Наличные", "Переводы"])].groupby("Категория")["Сумма операции"].sum().reset_index()
    transfers_and_cash["Сумма операции"] = -transfers_and_cash["Сумма операции"]
    transfers_and_cash = transfers_and_cash.to_dict("records")
    total_expenses = round(filtered["Сумма операции"].sum(), 2)
    return {
        "total_amount": total_expenses,
        "main": main_categories,
        "transfers_and_cash": transfers_and_cash
    }

def summarize_income(df, start_date, end_date):
    """Суммирование поступлений по категориям."""
    filtered = df[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date) & (df["Сумма операции"] > 0)]
    grouped = filtered.groupby("Категория")["Сумма операции"].sum().reset_index()
    main_categories = grouped.nlargest(7, "Сумма операции").to_dict("records")
    total_income = round(filtered["Сумма операции"].sum(), 2)
    return {
        "total_amount": total_income,
        "main": main_categories
    }
