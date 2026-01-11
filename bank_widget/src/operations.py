"""
Модуль для операций с банковскими транзакциями.
Содержит функции поиска и анализа транзакций.
"""

import logging
import re
from collections import Counter
from typing import Any, Dict, List, Optional, Pattern

# Создаем логгер для модуля operations
logger = logging.getLogger('bank_widget.operations')
logger.setLevel(logging.DEBUG)

# Убедимся, что у логгера нет обработчиков
if not logger.handlers:
    # Создаем путь к файлу логов
    from pathlib import Path
    current_dir = Path(__file__).parent  # src/
    project_root = current_dir.parent    # project_root/
    log_dir = project_root / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'operations.log'

    # Настраиваем file_handler
    file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # Настраиваем formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def search_transactions_by_description(
    transactions: List[Dict[str, Any]],
    search_string: str
) -> List[Dict[str, Any]]:
    """
    Ищет транзакции по заданной строке в описании с использованием регулярных выражений.

    Args:
        transactions: Список словарей с транзакциями
        search_string: Строка для поиска в описании транзакций

    Returns:
        Список словарей с транзакций, у которых в описании есть заданная строка

    Examples:
        >>> transactions = [{"description": "Перевод организации"}, {"description": "Оплата услуг"}]
        >>> search_transactions_by_description(transactions, "Перевод")
        [{"description": "Перевод организации"}]
    """
    logger.info(f"Поиск транзакций по строке: '{search_string}'")

    if not transactions:
        logger.warning("Пустой список транзакций для поиска")
        return []

    if not search_string:
        logger.warning("Пустая строка поиска")
        return transactions

    try:
        # Создаем регулярное выражение для поиска без учета регистра
        pattern = re.compile(re.escape(search_string), re.IGNORECASE)

        result = []
        for transaction in transactions:
            description = transaction.get('description', '')
            if description and pattern.search(description):
                result.append(transaction)

        logger.info(f"Найдено {len(result)} транзакций по строке '{search_string}'")
        return result

    except re.error as e:
        logger.error(f"Ошибка в регулярном выражении '{search_string}': {e}")
        # В случае ошибки в регулярном выражении, ищем простой подстрокой
        logger.info(f"Использую простой поиск для строки '{search_string}'")
        result = []
        for transaction in transactions:
            description = transaction.get('description', '').lower()
            if search_string.lower() in description:
                result.append(transaction)
        return result


def count_transactions_by_category(
    transactions: List[Dict[str, Any]],
    categories: List[str]
) -> Dict[str, int]:
    """
    Подсчитывает количество транзакций по категориям.

    Args:
        transactions: Список словарей с транзакциями
        categories: Список категорий для подсчета

    Returns:
        Словарь, где ключи - категории, значения - количество транзакций

    Examples:
        >>> transactions = [{"description": "Перевод организации"}, {"description": "Оплата услуг"}]
        >>> count_transactions_by_category(transactions, ["Перевод", "Оплата"])
        {"Перевод": 1, "Оплата": 1}
    """
    logger.info(f"Подсчет транзакций по категориям: {categories}")

    if not transactions:
        logger.warning("Пустой список транзакций для подсчета")
        return {category: 0 for category in categories}

    if not categories:
        logger.warning("Пустой список категорий для подсчета")
        return {}

    # Инициализируем счетчик с явной аннотацией типа
    counter: Counter[str] = Counter()

    # Создаем регулярные выражения для каждой категории
    # используем Optional[Pattern] так как может быть None в случае ошибки
    patterns: Dict[str, Optional[Pattern[str]]] = {}
    for category in categories:
        try:
            patterns[category] = re.compile(re.escape(category), re.IGNORECASE)
        except re.error as e:
            logger.error(f"Ошибка в регулярном выражении для категории '{category}': {e}")
            # В случае ошибки используем простое сравнение - ставим None
            patterns[category] = None

    # Подсчитываем транзакции по категориям
    for transaction in transactions:
        description = transaction.get('description', '').lower()
        if description:
            for category, pattern in patterns.items():
                if pattern is not None:
                    if pattern.search(description):
                        counter[category] += 1
                else:
                    # Простое сравнение без регулярного выражения
                    if category.lower() in description:
                        counter[category] += 1

    result = dict(counter)

    # Добавляем категории с нулевым количеством
    for category in categories:
        if category not in result:
            result[category] = 0

    logger.info(f"Результат подсчета: {result}")
    return result


def filter_transactions_by_currency(
    transactions: List[Dict[str, Any]],
    currency: str = "RUB"
) -> List[Dict[str, Any]]:
    """
    Фильтрует транзакции по валюте.

    Args:
        transactions: Список словарей с транзакциями
        currency: Код валюты для фильтрации (по умолчанию "RUB")

    Returns:
        Отфильтрованный список транзакций
    """
    logger.info(f"Фильтрация транзакций по валюте: {currency}")

    from .generators import filter_by_currency

    result = list(filter_by_currency(transactions, currency))
    logger.info(f"Найдено {len(result)} транзакций в валюте {currency}")
    return result


def format_transaction_for_display(transaction: Dict[str, Any]) -> str:
    """
    Форматирует транзакцию для вывода на экран.

    Args:
        transaction: Словарь с данными транзакции

    Returns:
        Отформатированная строка
    """
    try:
        from .widget import get_date, mask_account_card

        # Получаем дату
        date_str = get_date(transaction.get('date', ''))

        # Получаем описание
        description = transaction.get('description', 'Нет описания')

        # Форматируем отправителя и получателя
        from_str = transaction.get('from', '')
        to_str = transaction.get('to', '')

        if from_str:
            from_str = mask_account_card(from_str)
        if to_str:
            to_str = mask_account_card(to_str)

        # Получаем сумму и валюту
        operation_amount = transaction.get('operationAmount', {})
        amount = operation_amount.get('amount', '0')
        currency_info = operation_amount.get('currency', {})
        currency_name = currency_info.get('name', '')
        currency_code = currency_info.get('code', '')

        # Форматируем сумму
        if currency_name:
            amount_str = f"{amount} {currency_name} ({currency_code})"
        else:
            amount_str = f"{amount} {currency_code}"

        # Собираем строку
        result = f"{date_str} {description}\n"

        if from_str and to_str:
            result += f"{from_str} -> {to_str}\n"
        elif from_str:
            result += f"{from_str}\n"
        elif to_str:
            result += f"{to_str}\n"

        result += f"Сумма: {amount_str}\n"

        return result

    except Exception as e:
        logger.error(f"Ошибка форматирования транзакции: {e}")
        return f"Ошибка при форматировании транзакции: {transaction.get('id', 'N/A')}"
