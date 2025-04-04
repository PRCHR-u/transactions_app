import json
import logging
from datetime import datetime
from typing import Optional

import pandas as pd
import pytest

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def spending_by_category(df, category, date=None):
    """Расчет расходов по категории."""
    if date:
        df = df[df['Дата операции'].dt.strftime('%Y-%m-%d') <= date].copy()
    df_filtered = df[df['Категория'] == category]
    df_filtered = df_filtered[df_filtered['Сумма операции'] < 0]  # Только расходы
    category_spending = abs(df_filtered['Сумма операции'].sum())
    return {"category": category, "total": float(category_spending)}


def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> str:
    """Расчет средних трат по дням недели за последние 3 месяца.
    
    Args:
        transactions: DataFrame с транзакциями
        date: Опциональная дата, если не указана, берется текущая дата
        
    Returns:
        JSON строка со средними тратами по дням недели
    """
    logger.info("Начало расчета трат по дням недели")
    
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
        logger.info(f"Дата не указана, используется текущая дата: {date}")
    else:
        logger.info(f"Используется указанная дата: {date}")
    
    # Преобразуем дату в datetime
    end_date = pd.to_datetime(date)
    start_date = end_date - pd.DateOffset(months=3)
    logger.info(f"Период анализа: с {start_date} по {end_date}")
    
    # Создаем пустой DataFrame с нужными днями недели
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    result = pd.DataFrame(index=weekdays, columns=['mean', 'count'])
    result.fillna({'mean': 0.0, 'count': 0}, inplace=True)
    
    if transactions.empty:
        logger.warning("Получен пустой DataFrame с транзакциями")
        return json.dumps(result.to_dict(orient='index'), ensure_ascii=False)
    
    # Преобразуем даты в datetime если они еще не в этом формате
    transactions = transactions.copy()
    transactions['Дата операции'] = pd.to_datetime(transactions['Дата операции'])
    logger.info(f"Всего транзакций в исходном DataFrame: {len(transactions)}")
    
    # Фильтруем транзакции за последние 3 месяца
    df = transactions[
        (transactions['Дата операции'] >= start_date) & 
        (transactions['Дата операции'] <= end_date)
    ].copy()
    logger.info(f"Отфильтровано транзакций за указанный период: {len(df)}")
    
    # Фильтруем только расходы
    df = df[df['Сумма операции'] < 0]
    logger.info(f"Количество расходных операций: {len(df)}")
    
    # Добавляем колонку с днем недели
    df['weekday'] = df['Дата операции'].dt.day_name()
    
    if not df.empty:
        # Группируем по дню недели и считаем средние траты и количество
        grouped = df.groupby('weekday')['Сумма операции'].agg(['sum', 'count'])
        logger.debug("Сгруппированные данные по дням недели:\n%s", grouped)
        
        for day in weekdays:
            if day in grouped.index:
                # Считаем среднее значение как сумму, деленную на количество дней
                result.loc[day, 'mean'] = abs(grouped.loc[day, 'sum'])
                result.loc[day, 'count'] = grouped.loc[day, 'count']
                logger.debug(f"День {day}: сумма={result.loc[day, 'mean']}, количество={result.loc[day, 'count']}")
    
    # Округляем значения до 2 знаков
    result['mean'] = result['mean'].round(2)
    result['count'] = result['count'].astype(int)
    
    logger.info("Расчет трат по дням недели завершен успешно")
    # Преобразуем DataFrame в словарь и затем в JSON
    return json.dumps(result.to_dict(orient='index'), ensure_ascii=False)


def spending_by_workday(transactions: pd.DataFrame, date: Optional[str] = None) -> str:
    """Расчет средних трат в рабочий и выходной день за последние 3 месяца.
    
    Args:
        transactions: DataFrame с транзакциями
        date: Опциональная дата, если не указана, берется текущая дата
        
    Returns:
        JSON строка со средними тратами в рабочий и выходной день
    """
    logger.info("Начало расчета трат по рабочим/выходным дням")
    
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
        logger.info(f"Дата не указана, используется текущая дата: {date}")
    else:
        logger.info(f"Используется указанная дата: {date}")
    
    # Преобразуем дату в datetime
    end_date = pd.to_datetime(date)
    start_date = end_date - pd.DateOffset(months=3)
    logger.info(f"Период анализа: с {start_date} по {end_date}")
    
    # Создаем пустой DataFrame для результата
    result = pd.DataFrame(
        {'mean': [0.0, 0.0]},
        index=['Рабочий день', 'Выходной день']
    )
    
    if transactions.empty:
        logger.warning("Получен пустой DataFrame с транзакциями")
        return json.dumps(result.to_dict(orient='index'), ensure_ascii=False)
    
    # Преобразуем даты в datetime если они еще не в этом формате
    transactions = transactions.copy()
    transactions['Дата операции'] = pd.to_datetime(transactions['Дата операции'])
    logger.info(f"Всего транзакций в исходном DataFrame: {len(transactions)}")
    
    # Фильтруем транзакции за последние 3 месяца
    df = transactions[
        (transactions['Дата операции'] >= start_date) & 
        (transactions['Дата операции'] <= end_date)
    ].copy()
    logger.info(f"Отфильтровано транзакций за указанный период: {len(df)}")
    
    # Фильтруем только расходы
    df = df[df['Сумма операции'] < 0]
    logger.info(f"Количество расходных операций: {len(df)}")
    
    if not df.empty:
        # Определяем рабочие и выходные дни
        df['is_weekend'] = df['Дата операции'].dt.dayofweek.isin([5, 6])
        
        # Группируем по признаку выходного дня и считаем средние траты
        grouped = df.groupby('is_weekend')['Сумма операции'].agg(['sum', 'count'])
        logger.debug("Сгруппированные данные:\n%s", grouped)
        
        # Заполняем результат
        if False in grouped.index:  # Рабочие дни
            result.loc['Рабочий день', 'mean'] = abs(grouped.loc[False, 'sum'])
            logger.debug(f"Средние траты в рабочий день: {result.loc['Рабочий день', 'mean']}")
            
        if True in grouped.index:  # Выходные дни
            result.loc['Выходной день', 'mean'] = abs(grouped.loc[True, 'sum'])
            logger.debug(f"Средние траты в выходной день: {result.loc['Выходной день', 'mean']}")
    
    # Округляем значения до 2 знаков
    result['mean'] = result['mean'].round(2)
    
    logger.info("Расчет трат по рабочим/выходным дням завершен успешно")
    return json.dumps(result.to_dict(orient='index'), ensure_ascii=False)
