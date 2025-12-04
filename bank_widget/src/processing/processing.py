"""
Модуль обработки банковских операций.
"""

from typing import List, Dict, Any, Literal
from datetime import datetime


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
        >>> ops = [{'id': 1, 'state': 'EXECUTED'}, {'id': 2, 'state': 'CANCELED'}]
        >>> filter_by_state(ops)
        [{'id': 1, 'state': 'EXECUTED'}]
        >>> filter_by_state(ops, 'CANCELED')
        [{'id': 2, 'state': 'CANCELED'}]
    """
    if not operations:
        return []

    return [op for op in operations if op.get('state') == state]


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
        >>> sort_by_date(ops)
        [{'id': 2, 'date': '2023-01-02'}, {'id': 1, 'date': '2023-01-01'}]
    """
    if not operations:
        return []

    # Проверяем, что у всех операций есть дата
    valid_ops = [op for op in operations if 'date' in op]

    # Сортируем по дате
    try:
        return sorted(
            valid_ops,
            key=lambda x: datetime.fromisoformat(x['date']),
            reverse=reverse
        )
    except (ValueError, TypeError):
        # Если не удалось определить дату, возвращаем исходный список
        return operations