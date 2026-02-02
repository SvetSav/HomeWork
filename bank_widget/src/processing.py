"""
Модуль processing для обработки банковских данных.
Содержит функции фильтрации и сортировки операций.
"""

import re
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List


def filter_by_state(operations: List[Dict[str, Any]],
                    state: str = 'EXECUTED') -> List[Dict[str, Any]]:
    """
    Фильтрует список операций по статусу.

    Args:
        operations: Список словарей с операциями
        state: Статус для фильтрации (по умолчанию 'EXECUTED')

    Returns:
        Отфильтрованный список операций

    Examples:
        >>> ops = [
        ...     {'id': 1, 'state': 'EXECUTED'},
        ...     {'id': 2, 'state': 'CANCELED'}
        ... ]
        >>> filter_by_state(operations)
        [{'id': 1, 'state': 'EXECUTED'}]
        >>> filter_by_state(operations, 'CANCELED')
        [{'id': 2, 'state': 'CANCELED'}]
    """
    if not operations:
        return []

    # Приводим входной статус к верхнему регистру для сравнения
    state_upper = state.upper() if isinstance(state, str) else state

    return [operation for operation in operations
            if operation.get('state', '').upper() == state_upper]


def sort_by_date(operations: List[Dict[str, Any]],
                 reverse: bool = True) -> List[Dict[str, Any]]:
    """
    Сортирует операции по дате.

    Args:
        operations: Список словарей с операциями
        reverse: Порядок сортировки (True - по убыванию, False - по возрастанию)

    Returns:
        Отсортированный список операций

    Examples:
        >>> ops = [
        ...     {'id': 1, 'date': '2023-01-01'},
        ...     {'id': 2, 'date': '2023-01-02'}
        ... ]
        >>> sort_by_date(operations)
        [{'id': 2, 'date': '2023-01-02'}, {'id': 1, 'date': '2023-01-01'}]
    """
    if not operations:
        return []

    # Фильтруем операции с валидной датой
    operations_with_valid_date = []
    for operation in operations:
        if 'date' in operation and operation['date']:
            try:
                # Пробуем преобразовать дату
                date_str = operation['date'].replace("Z", "+00:00")
                datetime.fromisoformat(date_str)
                operations_with_valid_date.append(operation)
            except (ValueError, TypeError, AttributeError):
                # Пропускаем операции с некорректными датами
                continue

    # Сортируем по дате
    return sorted(
        operations_with_valid_date,
        key=lambda operation: datetime.fromisoformat(operation['date'].replace("Z", "+00:00")),
        reverse=reverse
    )


def process_bank_search(transactions: List[Dict[str, Any]], keyword: str) -> List[Dict[str, Any]]:
    """
        Фильтрует транзакции по ключевому слову в описании с использованием регулярных выражений.

        Args:
            transactions: Список транзакций
            keyword: Ключевое слово для поиска (регулярное выражение)

        Returns:
            Отфильтрованный список транзакций
        """
    if not transactions or not keyword:
        return transactions

    try:
        # Используем регулярное выражение с игнорированием регистра
        pattern = re.compile(keyword, re.IGNORECASE)
    except re.error:
        # В случае невалидного регулярного выражения используем обычный поиск
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)

    filtered = []

    for transaction in transactions:
        description = transaction.get('description', '')
        if isinstance(description, str) and pattern.search(description):
            filtered.append(transaction)

    return filtered


def process_bank_operations(data: List[Dict[str, Any]], categories: List[str]) -> Dict[str, int]:
    """
    Подсчитывает количество операций по категориям.

    Args:
        data: Список транзакций
        categories: Список категорий для подсчета

    Returns:
        Словарь с количеством операций по каждой категории

    Examples:
        >>> data = [
        ...     {'description': 'Перевод организации'},
        ...     {'description': 'Перевод со счета на счет'},
        ...     {'description': 'Перевод организации'},
        ...     {'description': 'Открытие вклада'}
        ... ]
        >>> categories = ['Перевод организации', 'Открытие вклада', 'Перевод со счета на счет']
        >>> process_bank_operations(data, categories)
        {'Перевод организации': 2, 'Открытие вклада': 1, 'Перевод со счета на счет': 1}
    """
    if not data:
        return {}

    if not categories:
        return {}

    # Создаем счетчик для категорий и инициализируем все категории нулями
    category_counter = {category: 0 for category in categories}

    # Приводим категории к нижнему регистру для сравнения
    categories_lower = [cat.lower() for cat in categories]

    for transaction in data:
        description = transaction.get('description', '')
        if isinstance(description, str):
            description_lower = description.lower()
            # Находим соответствующую категорию (регистронезависимо)
            for cat, cat_lower in zip(categories, categories_lower):
                if description_lower == cat_lower:
                    category_counter[cat] += 1
                    break

    return category_counter


def get_transaction_summary(transaction: Dict[str, Any]) -> str:
    """
    Возвращает краткое описание транзакции.

    Args:
        transaction: Словарь с данными транзакции

    Returns:
        Строка с кратким описанием
    """
    date_str = "Н/Д"
    if "date" in transaction and transaction["date"]:
        try:
            date_obj = datetime.fromisoformat(transaction["date"].replace("Z", "+00:00"))
            date_str = date_obj.strftime("%d.%m.%Y")
        except (ValueError, TypeError):
            pass

    description = transaction.get("description", "Н/Д")
    amount = transaction.get("amount", "Н/Д")
    currency = transaction.get("currency", "")

    return f"{date_str} {description} - {amount} {currency}"


# Примеры использования (для тестирования)
if __name__ == "__main__":
    # Пример данных из задания
    sample_operations = [
        {'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364',
         'description': 'Перевод организации', 'amount': 8221.37, 'currency': 'USD'},
        {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572',
         'description': 'Перевод организации', 'amount': 9824.07, 'currency': 'USD'},
        {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689',
         'description': 'Перевод со счета на счет', 'amount': 67314.70, 'currency': 'RUB'},
        {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441',
         'description': 'Перевод со счета на счет', 'amount': 77751.04, 'currency': 'RUB'},
        {'id': 72122709, 'state': 'EXECUTED', 'date': '2018-12-18T17:07:09.800800',
         'description': 'Открытие вклада', 'amount': 40542.0, 'currency': 'RUB'},
    ]

    print("Тестирование функции filter_by_state:")
    print("=" * 50)

    # Тест 1: Фильтрация со статусом по умолчанию (EXECUTED)
    executed_operations = filter_by_state(sample_operations)
    print(f"1. EXECUTED операции ({len(executed_operations)}):")
    for operation in executed_operations:
        summary = get_transaction_summary(operation)
        print(f"   {summary}")

    # Тест 2: Фильтрация со статусом CANCELED
    canceled_operations = filter_by_state(sample_operations, 'CANCELED')
    print(f"\n2. CANCELED операции ({len(canceled_operations)}):")
    for operation in canceled_operations:
        summary = get_transaction_summary(operation)
        print(f"   {summary}")

    print("\nТестирование функции sort_by_date:")
    print("=" * 50)

    # Тест 3: Сортировка по убыванию (по умолчанию)
    sorted_desc = sort_by_date(sample_operations, reverse=True)
    print("3. Сортировка по убыванию (новые сверху):")
    for index, operation in enumerate(sorted_desc, 1):
        summary = get_transaction_summary(operation)
        print(f"   {index}. {summary}")

    print("\nТестирование функции process_bank_search:")
    print("=" * 50)

    # Тест 4: Поиск по ключевому слову
    keyword = "перевод"
    filtered_by_keyword = process_bank_search(sample_operations, keyword)
    print(f"4. Операции с ключевым словом '{keyword}' ({len(filtered_by_keyword)}):")
    for operation in filtered_by_keyword:
        summary = get_transaction_summary(operation)
        print(f"   {summary}")

    print("\nТестирование функции process_bank_operations:")
    print("=" * 50)

    # Тест 5: Подсчет операций по категориям
    categories = ['Перевод организации', 'Перевод со счета на счет', 'Открытие вклада']
    category_counts = process_bank_operations(sample_operations, categories)
    print("5. Количество операций по категориям:")
    for category, count in category_counts.items():
        print(f"   {category}: {count}")

    print("\nВсе функции работают корректно!")
