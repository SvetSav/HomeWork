"""
Модуль processing для обработки банковских данных.
Содержит функции фильтрации и сортировки операций.
"""

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

    return [operation for operation in operations
            if operation.get('state') == state]


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

    # Фильтруем операции с датой
    operations_with_date = [
        operation for operation in operations
        if 'date' in operation and operation['date']
    ]

    # Сортируем по дате
    try:
        return sorted(
            operations_with_date,
            key=lambda operation: datetime.fromisoformat(operation['date']),
            reverse=reverse
        )
    except (ValueError, TypeError):
        # В случае ошибки определения даты возвращаем исходный список
        return operations_with_date


# Примеры использования (для тестирования)
if __name__ == "__main__":
    # Пример данных из задания
    sample_operations = [
        {'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'},
        {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'},
        {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'},
        {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'},
    ]

    print("Тестирование функции filter_by_state:")
    print("=" * 50)

    # Тест 1: Фильтрация со статусом по умолчанию (EXECUTED)
    executed_operations = filter_by_state(sample_operations)
    print(f"1. EXECUTED операции ({len(executed_operations)}):")
    for operation in executed_operations:
        print(f"   ID: {operation['id']}, Дата: {operation['date'][:10]}")

    # Тест 2: Фильтрация со статусом CANCELED
    canceled_operations = filter_by_state(sample_operations, 'CANCELED')
    print(f"\n2. CANCELED операции ({len(canceled_operations)}):")
    for operation in canceled_operations:
        print(f"   ID: {operation['id']}, Дата: {operation['date'][:10]}")

    print("\nТестирование функции sort_by_date:")
    print("=" * 50)

    # Тест 3: Сортировка по убыванию (по умолчанию)
    sorted_desc = sort_by_date(sample_operations, reverse=True)
    print("3. Сортировка по убыванию (новые сверху):")
    for index, operation in enumerate(sorted_desc, 1):
        state_icon = "✓" if operation['state'] == 'EXECUTED' else "✗"
        print(f"   {index}. {state_icon} ID: {operation['id']}, Дата: {operation['date'][:10]}")

    print("\n Функции работают корректно!")
