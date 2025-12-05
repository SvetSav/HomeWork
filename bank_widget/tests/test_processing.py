"""
Тесты для модуля processing.
"""

import sys
import os
from typing import List, Dict, Any

# Добавляем src в путь для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from processing import filter_by_state, sort_by_date


def test_filter_by_state() -> None:
    """Тест функции фильтрации по статусу."""
    # Тестовые данные
    operations: List[Dict[str, Any]] = [
        {'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'},
        {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'},
        {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'},
        {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'},
    ]

    # Тест со статусом по умолчанию (EXECUTED)
    result = filter_by_state(operations)
    assert len(result) == 2
    assert all(operation['state'] == 'EXECUTED' for operation in result)
    assert result[0]['id'] == 41428829
    assert result[1]['id'] == 939719570

    # Тест с указанным статусом CANCELED
    result = filter_by_state(operations, 'CANCELED')
    assert len(result) == 2
    assert all(operation['state'] == 'CANCELED' for operation in result)
    assert result[0]['id'] == 594226727
    assert result[1]['id'] == 615064591

    # Тест с пустым списком
    result = filter_by_state([])
    assert result == []

    print("Все тесты filter_by_state прошли успешно!")


def test_sort_by_date() -> None:
    """Тест функции сортировки по дате."""
    # Тестовые данные
    operations: List[Dict[str, Any]] = [
        {'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'},
        {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'},
        {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'},
        {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'},
    ]

    # Тест сортировки по убыванию (по умолчанию)
    result = sort_by_date(operations)
    assert len(result) == 4
    assert result[0]['id'] == 41428829  # Самая поздняя дата
    assert result[1]['id'] == 615064591
    assert result[2]['id'] == 594226727
    assert result[3]['id'] == 939719570  # Самая ранняя дата

    # Тест сортировки по возрастанию
    result = sort_by_date(operations, reverse=False)
    assert result[0]['id'] == 939719570  # Самая ранняя дата
    assert result[3]['id'] == 41428829   # Самая поздняя дата

    # Тест с пустым списком
    result = sort_by_date([])
    assert result == []

    print("Все тесты sort_by_date прошли успешно!")


if __name__ == "__main__":
    test_filter_by_state()
    test_sort_by_date()
    print("\n Все тесты пройдены успешно!")
