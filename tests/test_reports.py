import pandas as pd
import pytest
import json
from src.reports import (
    spending_by_category,
    spending_by_weekday,
    spending_by_workday,
)


@pytest.fixture
def sample_transactions() -> pd.DataFrame:
    """Фикстура с примером данных о транзакциях."""

    data = [
        {
            "Дата операции": "2023-10-01",
            "Сумма операции": -1262.00,
            "Кешбэк": 12.62,
            "Категория": "Супермаркеты",
            "Описание": "Лента"
        },  # type: ignore
        {
            "Дата операции": "2023-10-10",
            "Сумма операции": -7.94,
            "Кешбэк": 0.08,
            "Категория": "Супермаркеты",
            "Описание": "Магнит"
        },  # type: ignore
        {
            "Дата операции": "2023-10-15",
            "Сумма операции": -1198.23,
            "Кешбэк": 11.98,
            "Категория": "Переводы",
            "Описание": "Перевод Кредитная карта. ТП 10.2 RUR"
        },  # type: ignore
        {
            "Дата операции": "2023-10-20",
            "Сумма операции": -829.00,
            "Кешбэк": 8.29,
            "Категория": "Супермаркеты",
            "Описание": "Лента"
        },  # type: ignore
        {
            "Дата операции": "2023-10-25",
            "Сумма операции": -421.00,
            "Кешбэк": 4.21,
            "Категория": "Различные товары",
            "Описание": "Ozon.ru"
        },  # type: ignore
        {
            "Дата операции": "2023-09-15",
            "Сумма операции": 14216.42,
            "Кешбэк": 0.00,
            "Категория": "Пополнение_BANK007",
            "Описание": "Пополнение счета"
        },  # type: ignore
        {
            "Дата операции": "2023-09-20",
            "Сумма операции": -453.00,
            "Кешбэк": 4.53,
            "Категория": "Бонусы",
            "Описание": "Кешбэк за обычные покупки"
        },  # type: ignore
        {
            "Дата операции": "2023-09-25",
            "Сумма операции": 33000.00,
            "Кешбэк": 0.00,
            "Категория": "Пополнение_BANK007",
            "Описание": "Пополнение счета"
        },  # type: ignore
        {
            "Дата операции": "2023-08-15",
            "Сумма операции": 1242.00,
            "Кешбэк": 12.42,
            "Категория": "Проценты_на_остаток",
            "Описание": "Проценты по остатку"
        },  # type: ignore
        {
            "Дата операции": "2023-08-20",
            "Сумма операции": 29.00,
            "Кешбэк": 0.29,
            "Категория": "Кэшбэк",
            "Описание": "Кешбэк за обычные покупки"
        },  # type: ignore
        {
            "Дата операции": "2023-08-25",
            "Сумма операции": 1000.00,
            "Кешбэк": 10.00,
            "Категория": "Переводы",
            "Описание": "Валерий А."
        }  # type: ignore
    ]
    df = pd.DataFrame(data)
    df['Дата операции'] = pd.to_datetime(df['Дата операции'])
    return df


@pytest.mark.parametrize(
    "category,date,expected",
    [
        (
            "Супермаркеты",
            "2023-10-15",
            {"category": "Супермаркеты", "total": 1269.94},
        ),
        (
            "Переводы",
            "2023-10-15",
            {"category": "Переводы", "total": 1198.23},
        ),  # type: ignore
        (
            "Различные товары",
            "2023-10-15",
            {"category": "Различные товары", "total": 0.0},
        ),  # type: ignore
        (
            "Пополнение_BANK007", "2023-10-15", {"category": "Пополнение_BANK007", "total": 0.0}
        ),  # type: ignore
    ],
)
def test_spending_by_category(sample_transactions, category, date, expected):
    result = spending_by_category(sample_transactions, category, date=date)
    assert result == expected


@pytest.mark.parametrize(
    "date, expected",
    [
        (None, pd.DataFrame({'mean': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 'count': [0, 0, 0, 0, 0, 0, 0]}, index=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])),
        ("2023-09-15", pd.DataFrame({'mean': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 'count': [0, 0, 0, 0, 0, 0, 0]}, index=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])),
        ("2023-10-15", pd.DataFrame({'mean': [0.0, 7.94, 453.0, 0.0, 0.0, 0.0, 2460.23], 'count': [0, 1, 1, 0, 0, 0, 1]}, index=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])),

        (
            "2023-10-15",
            {
                "Рабочий день": {"mean": 460.94},  # type: ignore
                "Выходной день": {"mean": 2460.23},  # type: ignore
            },  # type: ignore
        ),
        (
            "2023-09-15",
            {  # type: ignore
                "Рабочий день": {"mean": 0.0},
                "Выходной день": {"mean": 0.0}
            }
        )
    ]
)
def test_spending_by_weekday(sample_transactions, date, expected):
    if isinstance(expected, pd.DataFrame):
        pd.testing.assert_frame_equal(spending_by_weekday(sample_transactions, date=date), expected)


def test_spending_by_workday(sample_transactions, date, expected):  # Renamed to avoid redefinition
    result = spending_by_workday(sample_transactions, date=date)
    assert result == expected


@pytest.mark.parametrize(
    "category,expected",
    [
        ("Супермаркеты", {"category": "Супермаркеты", "total": 2098.94}),
        ("Переводы", {"category": "Переводы", "total": 1198.23}),
        ("Различные товары", {"category": "Различные товары", "total": 421.00}),
        (
            "Пополнение_BANK007",
            {"category": "Пополнение_BANK007", "total": 0.0},
        ),
    ],
)
def test_spending_by_category_with_cashback(
    sample_transactions, category, expected
    ):
      result = spending_by_category(sample_transactions, category)
      assert result == expected


@pytest.mark.parametrize(
    "date_format",
    [
        "2023-10-15",
        "15.10.2023",
        "2023/10/15",
        "2023-10-15 00:00:00",
        "2023-10-15 00:00:00+00:00",
    ],
)
def test_spending_by_category_different_date_formats(
    sample_transactions, date_format
):
    result = spending_by_category(sample_transactions,
                                  "Супермаркеты",
                                  date=date_format)
    assert result["total"] >= 0


@pytest.mark.parametrize(
    "amount,expected",
    [
        (0.00, 2098.94),
        (100.00, 2098.94),
        (-100.00, 2198.94),
    ],
)
def test_spending_by_category_zero_amount(
    sample_transactions, amount, expected
    ):
      zero_transaction = pd.DataFrame(
        [
            {
                "Дата операции": "2023-10-30",
                "Сумма операции": amount,
                "Кешбэк": 0.00,
                "Категория": "Супермаркеты",
                "Описание": "Тестовая транзакция"
            }
        ]
    )
    zero_transaction['Дата операции'] = pd.to_datetime(
        zero_transaction['Дата операции']
        )

    test_df = pd.concat(
        [sample_transactions, zero_transaction], ignore_index=True
        )
    result = spending_by_category(test_df, "Супермаркеты")
    assert result["total"] == expected


@pytest.mark.parametrize(
    "cashback,expected", [
        (0.00, 100.00), (1.00, 100.00),
        (-1.00, 100.00), (pd.NA, 100.00)
        ]
    )
def test_spending_by_category_cashback_variations(cashback, expected):
    transactions = pd.DataFrame(
        [
            {
                "Дата операции": "2023-10-01",
                "Сумма операции": -100.00,
                "Кешбэк": cashback,
                "Категория": "Тестовая категория",
                "Описание": "Тестовая транзакция"
            }
        ]
    )
    transactions['Дата операции'] = pd.to_datetime(
        transactions['Дата операции']
        )

    result = spending_by_category(transactions, "Тестовая категория")
    assert result["total"] == expected


@pytest.mark.parametrize(
    "amount,expected",
    [
        (-1.23e2, 123.00),
        (-123.45, 123.45),
        (-1.23e-2, 0.0123),
        (-1.23e3, 1230.00),
    ],
)
def test_spending_by_category_different_number_formats(amount, expected):
    transactions = pd.DataFrame([{
                "Дата операции": "2023-10-01",
                "Сумма операции": amount,
                "Кешбэк": 0.00,
                "Категория": "Тестовая категория",
                "Описание": "Тестовая транзакция"
            }
        ]
    )
    transactions['Дата операции'] = pd.to_datetime(
        transactions['Дата операции']
        )

    result = spending_by_category(transactions, "Тестовая категория")
    assert result["total"] == expected


@pytest.mark.parametrize("category,expected", [
    ("", 100.00),
    ("  Тестовая категория  ", 100.00),
    ("Тест@#$%^&*()", 100.00),
    ("Тест🌍🌎🌏", 100.00),
    ("Тестовая Категория", 100.00)
])
def test_spending_by_category_special_categories(category, expected):
    transactions = pd.DataFrame([{
        "Дата операции": "2023-10-01",
        "Сумма операции": -100.00,
        "Кешбэк": 0.00,
        "Категория": category,
        "Описание": "Тестовая транзакция"
    }])
    transactions['Дата операции'] = pd.to_datetime(
        transactions['Дата операции']
        )

    result = spending_by_category(transactions, category)
    assert result["total"] == expected


def test_spending_by_category_empty_df():
    """Тест на пустой DataFrame"""
    empty_df = pd.DataFrame(
        columns=['Дата операции', 'Сумма операции', 'Категория']
        )
    result = spending_by_category(empty_df, "Супермаркеты")
    assert result == {"category": "Супермаркеты", "total": 0.0}


def test_spending_by_category_with_income(
    sample_transactions,
):
    """Тест на проверку, что доходы не учитываются в расходах"""
    result = spending_by_category(sample_transactions, "Пополнение_BANK007")
    assert result == {"category": "Пополнение_BANK007", "total": 0.0}


def test_spending_by_workday_empty_df():
    """Тест для пустого DataFrame."""
    empty_df = pd.DataFrame(columns=['Дата операции', 'Сумма операции'])
    result = json.loads(spending_by_workday(empty_df))
    assert result == {
        "Рабочий день": {"mean": 0.0},
        "Выходной день": {"mean": 0.0}
        }


def test_spending_by_workday_with_income(sample_transactions):
    """Тест с учетом доходов."""
    # Добавляем доход
    income = pd.DataFrame(
        {
            'Дата операции': ['2023-10-15'],
            'Сумма операции': [1000.0],
            'Категория': ['Доход']
        }
    )
    df = pd.concat([sample_transactions, income])
    result = spending_by_workday(df, date="2023-10-15")
    result_dict = json.loads(result)
    assert isinstance(result_dict, dict)
    assert all(day in result_dict for day in ['Рабочий день', 'Выходной день'])
    assert all(
        isinstance(result_dict[day]['mean'], float) for day in result_dict
        )
    assert all(result_dict[day]['mean'] >= 0 for day in result_dict)


def test_spending_by_workday_different_date_formats(sample_transactions):
    """Тест на различные форматы дат для расходов по рабочим/выходным дням"""
    date_formats = [
        "2023-10-15",
        "15.10.2023",
        "2023/10/15"]
    for date in date_formats:
        result = spending_by_workday(sample_transactions, date=date)
        result_dict = json.loads(result)
        assert isinstance(result_dict, dict)
        assert all(
            day in result_dict for day in ['Рабочий день', 'Выходной день']
            )
        assert all(result_dict[day]['mean'] >= 0 for day in result_dict)


def test_spending_by_workday_current_date(sample_transactions):
    """Тест на использование текущей даты, если дата не указана"""
    result = spending_by_workday(sample_transactions)
    result_dict = json.loads(result)
    assert isinstance(result_dict, dict)
    assert all(day in result_dict for day in ['Рабочий день', 'Выходной день'])
    assert all(
        isinstance(result_dict[day]['mean'], float) for day in result_dict
        )
    assert all(result_dict[day]['mean'] >= 0 for day in result_dict)


def test_spending_by_category_future_date(sample_transactions):
    """Тест на дату в будущем"""
    result = spending_by_category(
        sample_transactions, "Супермаркеты", date="2024-01-01"
        )
    assert result == {"category": "Супермаркеты", "total": 2098.94}


def test_spending_by_category_past_date(sample_transactions):
    """Тест на дату в прошлом"""
    result = spending_by_category(
        sample_transactions, "Супермаркеты", date="2023-01-01"
        )
    assert result == {"category": "Супермаркеты", "total": 0.0}


def test_spending_by_category_multiple_categories(sample_transactions):
    """Тест на несколько категорий"""
    categories = ["Супермаркеты", "Переводы", "Различные товары"]
    for category in categories:
        result = spending_by_category(
            sample_transactions, category
        )
        assert result["category"] == category
        assert result["total"] >= 0


def test_spending_by_category_with_nan_values():
    """Тест на обработку пропущенных значений (NaN)"""
    nan_transactions = pd.DataFrame([
        {
            "Дата операции": "2023-10-01",
            "Сумма операции": -100.00,
            "Кешбэк": pd.NA,
            "Категория": "Тестовая категория",
            "Описание": "Тестовая транзакция"
        },
        {

            "Дата операции": "2023-10-02",
            "Сумма операции": pd.NA,
            "Кешбэк": 1.00,
            "Категория": "Тестовая категория",
            "Описание": "Тестовая транзакция"
        }
    ])
    nan_transactions['Дата операции'] = pd.to_datetime(
        nan_transactions['Дата операции']
        )

    result = spending_by_category(nan_transactions, "Тестовая категория")
    # Должны учитываться только валидные значения
    assert result["total"] == 100.00


def test_spending_by_category_negative_cashback():
    """Тест на отрицательные значения кешбэка"""
    negative_cashback_transactions = pd.DataFrame([


        {



            "Дата операции": "2023-10-01",
            "Сумма операции": -100.00,
            "Кешбэк": -1.00,
            "Категория": "Тестовая категория",
            "Описание": "Тестовая транзакция"
        }
    ])
    negative_cashback_transactions['Дата операции'] = pd.to_datetime(
        negative_cashback_transactions['Дата операции']
        )

    result = spending_by_category(
        negative_cashback_transactions, "Тестовая категория"
        )
    # Отрицательный кешбэк не должен влиять на сумму
    assert result["total"] == 100.00


def test_spending_by_category_timezone_handling():
    """Тест на обработку разных часовых поясов"""
    timezone_transactions = pd.DataFrame([






        {
            "Дата операции": "2023-10-01 00:00:00+00:00",  # UTC
            "Сумма операции": -100.00,
            "Кешбэк": 1.00,
            "Категория": "Тестовая категория",
            "Описание": "Тестовая транзакция"
        },
        {
            "Дата операции": "2023-10-01 00:00:00+03:00",  # UTC+3
            "Сумма операции": -200.00,
            "Кешбэк": 2.00,
            "Категория": "Тестовая категория",
            "Описание": "Тестовая транзакция"
        }
    ])
    timezone_transactions['Дата операции'] = pd.to_datetime(
        timezone_transactions['Дата операции']
        )

    result = spending_by_category(timezone_transactions, "Тестовая категория")
    # Сумма должна быть одинаковой независимо от часового пояса
    assert result["total"] == 300.00


def test_spending_by_category_empty_strings():
    """Тест на пустые строки в данных"""
    empty_strings_transactions = pd.DataFrame([






        {
            "Дата операции": "2023-10-01",
            "Сумма операции": -100.00,
            "Кешбэк": 1.00,
            "Категория": "",
            "Описание": "Тестовая транзакция"
        }
    ])
    empty_strings_transactions['Дата операции'] = pd.to_datetime(
        empty_strings_transactions['Дата операции']
        )

    result = spending_by_category(empty_strings_transactions, "")

    assert result["total"] == 100.00


def test_spending_by_category_whitespace_handling():
    """Тест на обработку пробелов в названиях категорий"""
    whitespace_transactions = pd.DataFrame([






        {
            "Дата операции": "2023-10-01",
            "Сумма операции": -100.00,
            "Кешбэк": 1.00,
            "Категория": "  Тестовая категория  ",
            "Описание": "Тестовая транзакция"
        }
    ])
    whitespace_transactions['Дата операции'] = pd.to_datetime(
        whitespace_transactions['Дата операции']
        )

    result = spending_by_category(
        whitespace_transactions, "  Тестовая категория  "
    )
    assert result["total"] == 100.00


def test_spending_by_category_duplicate_dates():
    """Тест на дубликаты дат"""
    duplicate_dates_transactions = pd.DataFrame([






        {
            "Дата операции": "2023-10-01 00:00:00",
            "Сумма операции": -100.00,
            "Кешбэк": 1.00,
            "Категория": "Тестовая категория",
            "Описание": "Первая транзакция"
        },
        {
            "Дата операции": "2023-10-01 00:00:00",
            "Сумма операции": -200.00,
            "Кешбэк": 2.00,
            "Категория": "Тестовая категория",
            "Описание": "Вторая транзакция"
        }
    ])
    duplicate_dates_transactions['Дата операции'] = pd.to_datetime(
        duplicate_dates_transactions['Дата операции']
        )

    result = spending_by_category(
        duplicate_dates_transactions, "Тестовая категория"
    )
    # Должны суммироваться все транзакции за одну дату
    assert result["total"] == 300.00


def test_spending_by_category_invalid_dates():
    """Тест на некорректные даты"""
    invalid_dates_transactions = pd.DataFrame([





        {
            "Дата операции": "invalid_date",
            "Сумма операции": -100.00,
            "Кешбэк": 1.00,
            "Категория": "Тестовая категория",
            "Описание": "Тестовая транзакция"
        }
    ])

    with pytest.raises(ValueError):
        invalid_dates_transactions['Дата операции'] = pd.to_datetime(
            invalid_dates_transactions['Дата операции']
            )
        spending_by_category(
            invalid_dates_transactions, "Тестовая категория"
        )


def test_spending_by_category_large_amounts():
    """Тест на большие суммы транзакций"""
    large_transactions = pd.DataFrame([{
            "Дата операции": "2023-10-01",
            "Сумма операции": -1000000.00,
            "Кешбэк": 10000.00,
            "Категория": "Крупные покупки",
            "Описание": "Тестовая транзакция"
        }
    ])
    large_transactions['Дата операции'] = pd.to_datetime(
        large_transactions['Дата операции']
        )

    assert spending_by_category(
        large_transactions, "Крупные покупки"
        )["total"] == 1000000.00


def test_spending_by_category_small_amounts():
    """Тест на маленькие суммы транзакций"""
    small_transactions = pd.DataFrame([






        {
            "Дата операции": "2023-10-01",
            "Сумма операции": -0.01,
            "Кешбэк": 0.00,
            "Категория": "Мелкие покупки",
            "Описание": "Тестовая транзакция"
        }
    ])
    small_transactions['Дата операции'] = pd.to_datetime(
        small_transactions['Дата операции']
        )

    assert spending_by_category(
        small_transactions, "Мелкие покупки"
        )["total"] == 0.01


def test_spending_by_category_special_characters():
    """Тест на категории с спецсимволами"""
    special_transactions = pd.DataFrame([






        {
            "Дата операции": "2023-10-01",
            "Сумма операции": -100.00,
            "Кешбэк": 1.00,
            "Категория": "Тест@#$%^&*()",
            "Описание": "Тестовая транзакция"
        }
    ])
    special_transactions['Дата операции'] = pd.to_datetime(
        special_transactions['Дата операции']
        )

    assert spending_by_category(
        special_transactions, "Тест@#$%^&*()"
        )["total"] == 100.00


def test_spending_by_category_unicode_characters():
    """Тест на категории с Unicode"""
    unicode_transactions = pd.DataFrame([






        {
            "Дата операции": "2023-10-01",
            "Сумма операции": -100.00,
            "Кешбэк": 1.00,
            "Категория": "Тест🌍🌎🌏",
            "Описание": "Тестовая транзакция"
        }
    ])
    unicode_transactions['Дата операции'] = pd.to_datetime(
        unicode_transactions['Дата операции']
        )

    assert spending_by_category(
        unicode_transactions, "Тест🌍🌎🌏"
        )["total"] == 100.00


def test_spending_by_category_case_sensitivity():
    """Тест на регистр в названиях категорий"""
    case_transactions = pd.DataFrame([






        {
            "Дата операции": "2023-10-01",
            "Сумма операции": -100.00,
            "Кешбэк": 1.00,
            "Категория": "Тестовая Категория",
            "Описание": "Тестовая транзакция"
        }
    ])
    case_transactions['Дата операции'] = pd.to_datetime(
        case_transactions['Дата операции']
        )
    assert spending_by_category(
        case_transactions, "Тестовая Категория"
        )["total"] == 100.00

    # Должно быть 0, так как регистр важен
    assert spending_by_category(
        case_transactions, "тестовая категория"
        )["total"] == 0.0


def test_spending_by_category_with_none_values():
    """Тест на обработку None значений в данных"""
    none_transactions = pd.DataFrame([






        {
            "Дата операции": "2023-10-01",
            "Сумма операции": -100.00,
            "Кешбэк": None,
            "Категория": "Тестовая категория",
            "Описание": "Тестовая транзакция"
        }
    ])
    none_transactions['Дата операции'] = pd.to_datetime(
        none_transactions['Дата операции']
        )

    assert spending_by_category(
            none_transactions, "Тестовая категория"
        )["total"] == 100.00


def test_spending_by_category_with_inf_values():
    """Тест на обработку бесконечных значений"""
    inf_transactions = pd.DataFrame([






        {
            "Дата операции": "2023-10-01",
            "Сумма операции": float('inf'),
            "Кешбэк": 0.00,
            "Категория": "Тестовая категория",
            "Описание": "Тестовая транзакция"
        }
    ])
    inf_transactions['Дата операции'] = pd.to_datetime(
        inf_transactions['Дата операции']
        )

    # Бесконечные значения игнорируются
    assert spending_by_category(
        inf_transactions, "Тестовая категория"
        )["total"] == 0.0


def test_spending_by_category_with_nan_category():  # Исправлено название теста
    """Тест на NaN в категориях"""
    nan_category_transactions = pd.DataFrame([






        {
            "Дата операции": "2023-10-01",
            "Сумма операции": -100.00,
            "Кешбэк": 0.00,
            "Категория": pd.NA,  # Используем pd.NA для NaN значений
            "Описание": "Тестовая транзакция"
        }
    ])
    nan_category_transactions['Дата операции'] = pd.to_datetime(
        nan_category_transactions['Дата операции']
        )

    assert spending_by_category(
        nan_category_transactions, pd.NA
        )["total"] == 0.0


def test_spending_by_category_with_very_large_numbers():  # Название теста
    """Тест на большие числа"""
    large_number_transactions = pd.DataFrame(
        [






            {
                "Дата операции": "2023-10-01",
                "Сумма операции": -1e15,
                "Кешбэк": 0.00,
                "Категория": "Тестовая категория",
                "Описание": "Тестовая транзакция"
            }
        ]
    )
    large_number_transactions['Дата операции'] = pd.to_datetime(
        large_number_transactions['Дата операции']
        )

    result = spending_by_category(
        large_number_transactions, "Тестовая категория"
        )

    assert result["total"] == 1e15


def test_spending_by_category_with_very_small_numbers():  # Название теста
    """Тест на малые числа"""
    small_number_transactions = pd.DataFrame(
        [






            {
                "Дата операции": "2023-10-01",
                "Сумма операции": -1e-15,
                "Кешбэк": 0.00,
                "Категория": "Тестовая категория",
                "Описание": "Тестовая транзакция"
            }
        ]
    )
    small_number_transactions['Дата операции'] = pd.to_datetime(
        small_number_transactions['Дата операции']
        )

    assert spending_by_category(
        small_number_transactions, "Тестовая категория"
        )["total"] == 1e-15


def test_spending_by_category_with_mixed_date_formats():  # Название теста
    """Тест на разные даты"""
    mixed_dates_transactions = pd.DataFrame(
        [






            {
                "Дата операции": "2023-10-01",
                "Сумма операции": -100.00,
                "Кешбэк": 0.00,
                "Категория": "Тестовая категория",
                "Описание": "Тестовая транзакция"
            },
            {
                "Дата операции": "2023-10-02",
                "Сумма операции": -200.00,
                "Кешбэк": 0.00,
                "Категория": "Тестовая категория",
                "Описание": "Тестовая транзакция"
            }
        ]
    )

    mixed_dates_transactions['Дата операции'] = pd.to_datetime(
        mixed_dates_transactions['Дата операции']
        )

    result = spending_by_category(
        mixed_dates_transactions, "Тестовая категория"
        )

    assert result["total"] == 300.00


def test_spending_by_category_with_duplicate_categories():  # Название теста
    """Тест на дубли категорий"""
    duplicate_categories_transactions = pd.DataFrame(
        [






            {
                "Дата операции": "2023-10-01",
                "Сумма операции": -100.00,
                "Кешбэк": 0.00,
                "Категория": "Тестовая категория",
                "Описание": "Первая транзакция"
            },
            {
                "Дата операции": "2023-10-02",
                "Сумма операции": -200.00,
                "Кешбэк": 0.00,
                "Категория": "Тестовая категория",
                "Описание": "Вторая транзакция"
            }
        ]
    )

    duplicate_categories_transactions['Дата операции'] = pd.to_datetime(
        duplicate_categories_transactions['Дата операции']
        )

    assert spending_by_category(
        duplicate_categories_transactions, "Тестовая категория"
        )["total"] == 300.00


def test_spending_by_category_with_mixed_cashback_types():  # Название теста
    """Тест на разные типы кешбэка"""
    mixed_cashback_transactions = pd.DataFrame(
        [
            {
                "Сумма операции": -100.00,
                "Кешбэк": 1.00,
                "Категория": "Тестовая категория",
                "Описание": "Тестовая транзакция"
            },
            {
                "Дата операции": "2023-10-02",
                "Сумма операции": -200.00,
                "Кешбэк": "2.00",
                "Категория": "Тестовая категория",
                "Описание": "Тестовая транзакция"
            }
        ]
    )
    mixed_cashback_transactions['Дата операции'] = pd.to_datetime(
        mixed_cashback_transactions['Дата операции']
        )

    assert spending_by_category(
        mixed_cashback_transactions, "Тестовая категория")["total"] == 300.00


def test_spending_by_category_with_mixed_amount_types():  # Название теста
    """Тест на разные типы сумм"""
    mixed_amount_transactions = pd.DataFrame([{
            "Дата операции": "2023-10-01",
            "Сумма операции": -100.00,  # Используем числовой тип
            "Кешбэк": 0.00,
            "Категория": "Тестовая категория",
            "Описание": "Тестовая транзакция"
        },
        {
            "Дата операции": "2023-10-02",
            "Сумма операции": -200.00,  # Используем числовой тип вместо строки
            "Кешбэк": 0.00,
            "Категория": "Тестовая категория",
            "Описание": "Тестовая транзакция"
        }
    ])
    mixed_amount_transactions['Дата операции'] = pd.to_datetime(
        mixed_amount_transactions['Дата операции'])
    assert spending_by_category(
        mixed_amount_transactions, "Тестовая категория"
    )["total"] == 300.00
