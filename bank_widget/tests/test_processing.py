"""
Тесты для модуля processing.
"""

import sys
import os

# Добавляем src в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Импортируем из пакета
from bank_widget import filter_by_state, sort_by_date


def test_filter_by_state():
    """Тест функции фильтрации по статусу."""

    # Тест со статусом по умолчанию
    result = filter_by_state()
    assert len(result) == 2
    assert all(op['state'] == 'EXECUTED' for op in result)

    # Тест с указанным статусом
    result = filter_by_state()
    assert len(result) == 2
    assert all(op['state'] == 'CANCELED' for op in result)

    print('test_filter_by_state passed')


def test_sort_by_date():
    """Тест функции сортировки по дате."""

    # Сортировка по убыванию
    result = sort_by_date()
    assert result[0]['id'] == 41428829  # Самая поздняя

    # Сортировка по возрастанию
    result = sort_by_date()
    assert result[0]['id'] == 939719570  # Самая ранняя

    print("test_sort_by_date passed")


if __name__ == "__main__":
    test_filter_by_state()
    test_sort_by_date()
    print("\n Все тесты пройдены!")