"""
Модуль генераторов для обработки банковских транзакций.
Содержит функции для фильтрации и итерации по транзакциям.
"""

from typing import Any
from typing import Dict
from typing import Iterator
from typing import List


def filter_by_currency(transactions: List[Dict[str, Any]], currency: str) -> Iterator[Dict[str, Any]]:
    currency_upper = currency.upper()  # Приводим к верхнему регистру
    for transaction in transactions:
        transaction_currency = transaction.get('currency', '')
        if isinstance(transaction_currency, str):
            if transaction_currency.upper() == currency_upper:
                yield transaction
                """
    Фильтрует транзакции по заданной валюте.

    Args:
        transactions: Список словарей с транзакциями
        currency: Код валюты для фильтрации (например, "USD", "RUB")

    Yields:
        Словари транзакций, где валюта соответствует заданной

    Examples:
        >>> transactions = [
        ...     {"id": 1, "operationAmount": {"currency": {"code": "USD"}}},
        ...     {"id": 2, "operationAmount": {"currency": {"code": "RUB"}}}
        ... ]
        >>> usd_transactions = filter_by_currency(transactions, "USD")
        >>> next(usd_transactions)["id"]
        1
    """
    for transaction in transactions:
        try:
            if transaction.get("operationAmount", {}).get("currency", {}).get("code") == currency:
                yield transaction
        except (AttributeError, KeyError):
            continue


def transaction_descriptions(transactions: List[Dict[str, Any]]) -> Iterator[str]:
    """
    Генератор описаний транзакций.

    Args:
        transactions: Список словарей с транзакциями

    Yields:
        Описание каждой транзакции

    Examples:
        >>> transactions = [
        ...     {"description": "Перевод организации"},
        ...     {"description": "Оплата услуг"}
        ... ]
        >>> desc_gen = transaction_descriptions(transactions)
        >>> next(desc_gen)
        'Перевод организации'
    """
    for transaction in transactions:
        description = transaction.get("description")
        if description:
            yield description


def card_number_generator(start: int, end: int) -> Iterator[str]:
    """
    Генератор номеров банковских карт.

    Args:
        start: Начальный номер карты (от 1)
        end: Конечный номер карты (до 9999999999999999)

    Yields:
        Номер карты в формате "XXXX XXXX XXXX XXXX"

    Examples:
        >>> gen = card_number_generator(1, 3)
        >>> list(gen)
        ['0000 0000 0000 0001', '0000 0000 0000 0002', '0000 0000 0000 0003']
    """
    if start < 1:
        raise ValueError("Начальное значение должно быть не менее 1")
    if end > 9999999999999999:
        raise ValueError("Конечное значение не должно превышать 9999999999999999")
    if start > end:
        raise ValueError("Начальное значение должно быть меньше или равно конечному")

    for number in range(start, end + 1):
        # Форматируем номер: 16 цифр с ведущими нулями
        card_str = f"{number:016d}"
        # Разделяем на группы по 4 цифры
        formatted = f"{card_str[:4]} {card_str[4:8]} {card_str[8:12]} {card_str[12:]}"
        yield formatted
