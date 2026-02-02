"""
Тесты для модуля processing.
"""

import sys
from builtins import len

import pytest
from processing import filter_by_state
from processing import process_bank_operations
from processing import process_bank_search
from processing import sort_by_date

# Добавляем src в путь для импорта
sys.path.insert(0, sys.path[0] + '/../src')


# Фикстуры
@pytest.fixture
def sample_operations():
    """Фикстура с тестовыми операциями."""
    return [
        {'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364',
         'description': 'Перевод организации'},
        {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572',
         'description': 'Перевод организации'},
        {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689',
         'description': 'Перевод со счета на счет'},
        {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441',
         'description': 'Перевод со счета на счет'},
        {'id': 123, 'state': 'PENDING', 'date': '2019-01-01T00:00:00.000000',
         'description': 'Открытие вклада'},
        {'id': 456, 'state': 'EXECUTED', 'date': '2020-01-01T00:00:00.000000',
         'description': 'Оплата услуг'},
        {'id': 789, 'date': '2020-01-02T00:00:00.000000'},  # Без статуса
    ]


@pytest.fixture
def operations_with_duplicate_dates():
    """Фикстура с операциями с одинаковыми датами."""
    return [
        {'id': 1, 'state': 'EXECUTED', 'date': '2024-01-01T00:00:00.000000',
         'description': 'Операция 1'},
        {'id': 2, 'state': 'EXECUTED', 'date': '2024-01-01T00:00:00.000000',
         'description': 'Операция 2'},
        {'id': 3, 'state': 'EXECUTED', 'date': '2024-01-01T00:00:00.000000',
         'description': 'Операция 3'},
    ]


@pytest.fixture
def operations_with_invalid_dates():
    """Фикстура с операциями с некорректными датами."""
    return [
        {'id': 1, 'state': 'EXECUTED', 'date': 'invalid-date',
         'description': 'Операция 1'},
        {'id': 2, 'state': 'EXECUTED', 'date': '',
         'description': 'Операция 2'},
        {'id': 3, 'state': 'EXECUTED', 'date': None,
         'description': 'Операция 3'},
    ]


# Параметризация тестов для filter_by_state
@pytest.mark.parametrize("state, expected_count", [
    ('EXECUTED', 3),  # 41428829, 939719570, 456
    ('executed', 3),  # регистронезависимый
    ('CANCELED', 2),  # 594226727, 615064591
    ('canceled', 2),  # регистронезависимый
    ('PENDING', 1),  # 123
    ('NONEXISTENT', 0),
])
def test_filter_by_state_parametrized(sample_operations, state, expected_count):
    """Параметризованный тест фильтрации по статусу."""
    result = filter_by_state(sample_operations, state)
    assert len(result) == expected_count
    if expected_count > 0:
        # Функция приводит state к верхнему регистру, поэтому сравниваем с верхним регистром
        assert all(operation['state'].upper() == state.upper() for operation in result)


def test_filter_by_state_default(sample_operations):
    """Тест фильтрации со статусом по умолчанию."""
    result = filter_by_state(sample_operations)  # default = 'EXECUTED'
    assert len(result) == 3
    assert all(operation['state'] == 'EXECUTED' for operation in result)


def test_filter_by_state_empty() -> None:
    """Тест фильтрации пустого списка."""
    result = filter_by_state([])
    assert result == []


def test_filter_by_state_no_state_field() -> None:
    """Тест фильтрации операций без поля state."""
    operations = [
        {'id': 1, 'date': '2024-01-01T00:00:00.000000'},
        {'id': 2, 'date': '2024-01-02T00:00:00.000000'},
    ]
    result = filter_by_state(operations, 'EXECUTED')
    assert result == []


def test_filter_by_state_with_none_operations() -> None:
    """Тест фильтрации когда operations = None."""
    result = filter_by_state([])
    assert result == []


def test_filter_by_state_with_invalid_operations() -> None:
    """Тест фильтрации с некорректными данными."""
    result = filter_by_state([{'id': 1}], 'EXECUTED')
    assert result == []


# Параметризация тестов для sort_by_date
@pytest.mark.parametrize("reverse, expected_count", [
    (True, 7),  # descending (newest first) - все 7 операций с валидными датами
    (False, 7),  # ascending (oldest first) - все 7 операций с валидными датами
])
def test_sort_by_date_parametrized(sample_operations, reverse, expected_count):
    """Параметризованный тест сортировки по дате."""
    result = sort_by_date(sample_operations, reverse=reverse)
    assert len(result) == expected_count

    if result:
        # Проверяем что даты отсортированы правильно
        dates = [operation['date'] for operation in result]
        if reverse:
            # Убедимся что сортировка по убыванию работает
            sorted_dates = sorted(dates, reverse=True)
            assert dates == sorted_dates
        else:
            # Убедимся что сортировка по возрастанию работает
            sorted_dates = sorted(dates)
            assert dates == sorted_dates


def test_sort_by_date_empty() -> None:
    """Тест сортировки пустого списка."""
    result = sort_by_date([])
    assert result == []


def test_sort_by_date_duplicate_dates(operations_with_duplicate_dates):
    """Тест сортировки с одинаковыми датами."""
    result = sort_by_date(operations_with_duplicate_dates)
    # Все операции с одинаковыми датами должны остаться
    assert len(result) == len(operations_with_duplicate_dates)
    # При одинаковых датах порядок не важен, но все даты должны быть одинаковыми
    assert all(op['date'] == '2024-01-01T00:00:00.000000' for op in result)


def test_sort_by_date_invalid_dates(operations_with_invalid_dates):
    """Тест сортировки с некорректными датами."""
    result = sort_by_date(operations_with_invalid_dates)
    # Операции с некорректными датами должны быть отфильтрованы
    assert len(result) == 0
    assert isinstance(result, list)


def test_sort_by_date_no_date_field() -> None:
    """Тест сортировки операций без поля date."""
    operations = [
        {'id': 1, 'state': 'EXECUTED'},
        {'id': 2, 'state': 'EXECUTED'},
        {'id': 3, 'state': 'EXECUTED', 'date': '2024-01-01T00:00:00.000000'},
    ]
    result = sort_by_date(operations)
    # Должна остаться только операция с валидной датой
    assert len(result) == 1
    assert result[0]['id'] == 3


def test_module_execution(capsys):
    """Прямой тест выполнения модуля."""
    import importlib.util
    import os

    file_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'processing.py')

    spec = importlib.util.spec_from_file_location("__main__", file_path)
    if spec is None:
        pytest.skip(f"Не удалось создать спецификацию для {file_path}")
        return  # type: ignore[unreachable]

    module = importlib.util.module_from_spec(spec)

    if spec.loader is None:
        pytest.skip(f"Loader не найден для {file_path}")
        return  # type: ignore[unreachable]

    spec.loader.exec_module(module)

    # Получаем вывод
    captured = capsys.readouterr()
    output = captured.out

    # Проверяем вывод
    assert "Тестирование функции filter_by_state" in output
    assert "Все функции работают корректно!" in output
    assert "EXECUTED операции" in output
    assert "CANCELED операции" in output


# Тесты для process_bank_search (с регулярными выражениями)
def test_process_bank_search_basic():
    """Тест базового поиска по ключевому слову."""
    transactions = [
        {'id': 1, 'description': 'Перевод организации'},
        {'id': 2, 'description': 'Открытие вклада'},
        {'id': 3, 'description': 'Перевод со счета на счет'},
        {'id': 4, 'description': 'Перевод организации'},
    ]

    result = process_bank_search(transactions, 'перевод')
    assert len(result) == 3
    assert all('перевод' in t['description'].lower() for t in result)


def test_process_bank_search_case_insensitive():
    """Тест регистронезависимого поиска."""
    transactions = [
        {'id': 1, 'description': 'Перевод организации'},
        {'id': 2, 'description': 'ПЕРЕВОД со счета'},
        {'id': 3, 'description': 'перевод вклада'},
        {'id': 4, 'description': 'Оплата услуг'},
    ]

    result = process_bank_search(transactions, 'ПЕРЕВОД')
    assert len(result) == 3


def test_process_bank_search_regex():
    """Тест поиска с использованием регулярных выражений."""
    transactions = [
        {'id': 1, 'description': 'Перевод организации 123'},
        {'id': 2, 'description': 'Перевод физического лица'},
        {'id': 3, 'description': 'Открытие вклада 456'},
        {'id': 4, 'description': 'Перевод организации ABC'},
    ]

    # Поиск по паттерну: "Перевод" + пробел + слово
    result = process_bank_search(transactions, 'Перевод\\s+\\w+')
    assert len(result) == 3


def test_process_bank_search_empty():
    """Тест поиска с пустыми данными."""
    assert process_bank_search([], 'перевод') == []
    assert process_bank_search([{'id': 1}], '') == [{'id': 1}]


def test_process_bank_search_no_description():
    """Тест поиска в транзакциях без описания."""
    transactions = [
        {'id': 1},
        {'id': 2, 'description': None},
        {'id': 3, 'description': ''},
        {'id': 4, 'description': 'Перевод'},
    ]

    result = process_bank_search(transactions, 'перевод')
    assert len(result) == 1
    assert result[0]['id'] == 4


# Тесты для process_bank_operations
def test_process_bank_operations_basic():
    """Тест базового подсчета операций по категориям."""
    data = [
        {'description': 'Перевод организации'},
        {'description': 'Перевод со счета на счет'},
        {'description': 'Перевод организации'},
        {'description': 'Открытие вклада'},
        {'description': 'Перевод организации'},
    ]

    categories = ['Перевод организации', 'Открытие вклада', 'Перевод со счета на счет']

    result = process_bank_operations(data, categories)

    assert result == {
        'Перевод организации': 3,
        'Открытие вклада': 1,
        'Перевод со счета на счет': 1
    }


def test_process_bank_operations_case_insensitive():
    """Тест регистронезависимого подсчета."""
    data = [
        {'description': 'перевод организации'},
        {'description': 'ПЕРЕВОД ОРГАНИЗАЦИИ'},
        {'description': 'Перевод Организации'},
        {'description': 'открытие вклада'},
    ]

    categories = ['Перевод организации', 'Открытие вклада']

    result = process_bank_operations(data, categories)

    assert result == {
        'Перевод организации': 3,
        'Открытие вклада': 1
    }


def test_process_bank_operations_empty():
    """Тест подсчета с пустыми данными."""
    assert process_bank_operations([], []) == {}
    assert process_bank_operations([{'description': 'Test'}], []) == {}
    assert process_bank_operations([], ['Test']) == {}


def test_process_bank_operations_no_match():
    """Тест подсчета без совпадений."""
    data = [
        {'description': 'Перевод организации'},
        {'description': 'Открытие вклада'},
    ]

    categories = ['Оплата услуг', 'Пополнение счета']

    result = process_bank_operations(data, categories)

    # Теперь функция должна возвращать словарь с нулями
    assert result == {'Оплата услуг': 0, 'Пополнение счета': 0}


def test_process_bank_operations_uses_counter():
    """Тест что функция использует Counter."""
    data = [{'description': 'Перевод организации'} for _ in range(10)]
    categories = ['Перевод организации']

    result = process_bank_operations(data, categories)

    # Проверяем что результат правильный
    assert result == {'Перевод организации': 10}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
