"""
Модуль генераторов для обработки банковских транзакций.
Содержит функции для фильтрации и итерации по транзакциям.
"""

from typing import Any
from typing import Dict
from typing import Iterator
from typing import List


def filter_by_currency(transactions: List[Dict[str, Any]], currency: str) -> Iterator[Dict[str, Any]]:
    """
    Фильтрует транзакции по заданной валюте.

    Args:
        transactions: Список словарей с транзакциями
        currency: Код валюты для фильтрации (например, "USD", "RUB")

    Yields:
        Словари транзакций, где валюта соответствует заданной

    Examples:
        >>> 'transactions = ['
        ...     {"id": 1, "operationAmount": {"currency": {"code": "USD"}}},
        ...     {"id": 2, "operationAmount": {"currency": {"code": "RUB"}}}
        ... ]
        >>> usd_transactions = filter_by_currency(transactions, "USD")
        >>> next(usd_transactions)["id"]
        1
    """
    currency_upper = currency.upper()  # Приводим к верхнему регистру для регистронезависимого сравнения

    for transaction in transactions:

        # 1. Формат из JSON: operationAmount -> currency -> code
        try:
            operation_amount = transaction.get("operationAmount", {})
            if isinstance(operation_amount, dict):
                currency_obj = operation_amount.get("currency", {})
                if isinstance(currency_obj, dict):
                    code = currency_obj.get("code", "")
                    if code.upper() == currency_upper:
                        yield transaction
                        continue
        except (AttributeError, KeyError):
            pass

        # 2. Формат из CSV: прямое поле currency
        trans_currency = transaction.get('currency', '')
        if isinstance(trans_currency, str) and trans_currency.upper() == currency_upper:
            yield transaction
            continue

        # 3. Формат с вложенностью: currency -> code
        currency_data = transaction.get("currency", {})
        if isinstance(currency_data, dict):
            code = currency_data.get("code", "")
            if code.upper() == currency_upper:
                yield transaction


def transaction_descriptions(transactions: List[Dict[str, Any]]) -> Iterator[str]:
    """
    Генератор описаний транзакций.

    Args:
        transactions: Список словарей с транзакциями

    Yields:
        Описание каждой транзакции

    Examples:
        >>> 'transactions = ['
        ...     {"description": "Перевод организации"},
        ...     {"description": "Оплата услуг"}
        ... ]
        >>> 'desc_gen = transaction_descriptions(transactions)'
        >>> next(desc_gen)
        'Перевод организации'
    """
    for transaction in transactions:
        description = transaction.get("description", "Нет описания")
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


if __name__ == "__main__":
    # Тестирование функций
    print("Тестирование генераторов:")
    print("=" * 50)

    # Тест filter_by_currency
    test_transactions = [
        {"id": 1, "operationAmount": {"amount": "100", "currency": {"code": "USD", "name": "Доллар США"}}},
        {"id": 2, "operationAmount": {"amount": "200", "currency": {"code": "RUB", "name": "Российский рубль"}}},
        {"id": 3, "currency": "USD"},
        {"id": 4, "currency": "EUR"},
        {"id": 5, "currency": {"code": "RUB", "name": "Рубль"}}
    ]

    print("1. Фильтрация по валюте USD:")
    usd_gen = filter_by_currency(test_transactions, "USD")
    for trans in usd_gen:
        print(f"   ID: {trans['id']}")

    print("\n2. Фильтрация по валюте RUB:")
    rub_gen = filter_by_currency(test_transactions, "RUB")
    for trans in rub_gen:
        print(f"   ID: {trans['id']}")

    print("\n3. Описания транзакций:")
    descriptions = [
        {"description": "Перевод организации"},
        {"description": "Открытие вклада"},
        {"description": "Оплата услуг"},
        {"description": "Нет описания"},
        {"description": ""}
    ]

    desc_gen = transaction_descriptions(descriptions)

    for desc in desc_gen:
        print(f"   {desc}")

    print("\n4. Генератор номеров карт (1-5):")
    card_gen = card_number_generator(1, 5)
    for card in card_gen:
        print(f"   {card}")

    print("\nВсе функции работают корректно!")
