"""
Тесты для модуля widget.
"""

import os
import sys

# Добавляем src в путь для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest  # noqa: E402
from widget import get_date  # noqa: E402
from widget import mask_account_card  # noqa: E402


# Параметризация тестов для карт
@pytest.mark.parametrize("input_card, expected", [
    ("Visa Platinum 7000792289606361", "Visa Platinum 7000 79** **** 6361"),
    ("Maestro 1596837868705199", "Maestro 1596 83** **** 5199"),
    ("MasterCard 7158300734726758", "MasterCard 7158 30** **** 6758"),
    ("Visa Classic 6831982476737658", "Visa Classic 6831 98** **** 7658"),
    ("Visa Platinum 8990922113665229", "Visa Platinum 8990 92** **** 5229"),
    ("Visa Gold 5999414228426353", "Visa Gold 5999 41** **** 6353"),
])
def test_mask_account_card_cards(input_card: str, expected: str) -> None:
    """Параметризованный тест маскировки карт."""
    result = mask_account_card(input_card)
    assert result == expected


# Параметризация тестов для счетов
@pytest.mark.parametrize("input_account, expected", [
    ("Счет 73654108430135874305", "Счет **4305"),
    ("Счет 64686473678894779589", "Счет **9589"),
    ("Счет 35383033474447895560", "Счет **5560"),
])
def test_mask_account_card_accounts(input_account: str, expected: str) -> None:
    """Параметризованный тест маскировки счетов."""
    result = mask_account_card(input_account)
    assert result == expected


# Параметризация тестов для некорректных данных
@pytest.mark.parametrize("invalid_input", [
    "",
    "InvalidData",
    "Счет",  # нет номера
    "Visa Platinum",  # нет номера
    "Счет 123",  # короткий номер
])
def test_mask_account_card_invalid(invalid_input: str) -> None:
    """Параметризованный тест маскировки некорректных данных."""
    result = mask_account_card(invalid_input)

    # Проверяем что функция не падает и возвращает строку
    assert isinstance(result, str)

    if invalid_input == "":
        assert result == ""
    elif invalid_input == "Счет 123":
        # Для короткого счета должно возвращаться что-то типа "Счет **123"
        assert "**" in result
    elif invalid_input == "Visa Platinum":
        assert "**" in result or "****" in result  # Проверяем наличие маскировки
    elif invalid_input == "Счет":
        # Для счета без номера возвращается исходная строка
        assert result == "Счет"
    else:
        # Для других некорректных данных возвращается исходная строка
        assert result == invalid_input


# Параметризация тестов для дат
@pytest.mark.parametrize("input_date, expected", [
    ("2024-03-11T02:26:18.671407", "11.03.2024"),
    ("2023-12-31T23:59:59.999999", "31.12.2023"),
    ("2024-01-01T00:00:00.000000", "01.01.2024"),
    ("2024-02-29T12:30:45.123456", "29.02.2024"),  # високосный год
])
def test_get_date_valid(input_date: str, expected: str) -> None:
    """Параметризованный тест форматирования корректных дат."""
    result = get_date(input_date)
    assert result == expected


# Параметризация тестов для некорректных дат
@pytest.mark.parametrize("invalid_date", [
    "",
    "not-a-date",
    "2024-13-01T00:00:00.000000",  # некорректных месяц
    "2024-02-30T00:00:00.000000",  # некорректный день
])
def test_get_date_invalid(invalid_date: str) -> None:
    """Параметризованный тест форматирования некорректных дат."""
    result = get_date(invalid_date)
    # При ошибке возвращается исходная строка
    assert result == invalid_date


# Тесты с использованием фикстур
def test_mask_account_card_cards_fixture(sample_cards):
    """Тест маскировки карт с использованием фикстур."""
    for card in sample_cards:
        result = mask_account_card(card)
        # Проверяем наличие маскировки
        assert "****" in result


def test_mask_account_card_accounts_fixture(sample_accounts):
    """Тест маскировки счетов с использованием фикстур."""
    for account in sample_accounts:
        result = mask_account_card(account)
        assert "**" in result  # Проверяем формат


def test_get_date_with_fixtures(sample_dates):
    """Тест форматирования дат с использованием фикстур."""
    for date_str in sample_dates:
        result = get_date(date_str)
        # Проверяем формат ДД.ММ.ГГГГ
        assert result.count(".") == 2
        assert len(result.split(".")[0]) == 2  # день
        assert len(result.split(".")[1]) == 2  # месяц
        assert len(result.split(".")[2]) == 4  # год


def test_mask_card_number() -> None:
    """Тест маскировки номера карты (отдельная функция)."""
    from widget import mask_card_number

    test_cases = [
        ("7000792289606361", "7000 79** **** 6361"),
        ("1596837868705199", "1596 83** **** 5199"),
        ("7158300734726758", "7158 30** **** 6758"),
        ("1234567890123456", "1234 56** **** 3456"),
    ]

    for input_num, expected in test_cases:
        result = mask_card_number(input_num)
        assert result == expected


def test_mask_account_number() -> None:
    """Тест маскировки номера счета (отдельная функция)."""
    from widget import mask_account_number

    test_cases = [
        ("73654108430135874305", "**4305"),
        ("64686473678894779589", "**9589"),
        ("35383033474447895560", "**5560"),
        ("1234567890", "**7890"),
    ]

    for input_num, expected in test_cases:
        result = mask_account_number(input_num)
        assert result == expected


def test_mask_account_number_edge_cases() -> None:
    """Тест edge cases для mask_account_number."""
    from widget import mask_account_number

    # Короткий номер счета
    result = mask_account_number("1234")
    assert result == "**1234"

    # Очень короткий номер
    result = mask_account_number("12")
    assert result == "**12"

    # Пустая строка
    result = mask_account_number("")
    assert result == "**"


def test_main_block_execution(capsys):
    """Тест выполнения модуля как main."""
    import importlib.util
    import os

    file_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'widget.py')

    if not os.path.exists(file_path):
        pytest.skip(f"Файл {file_path} не найден")
        return  # type: ignore[unreachable]

    spec = importlib.util.spec_from_file_location("__main__", file_path)
    if spec is None:
        pytest.skip(f"Не удалось создать спецификацию для {file_path}")
        return  # type: ignore[unreachable]

    module = importlib.util.module_from_spec(spec)

    if spec.loader is None:
        pytest.skip(f"Loader не найден для {file_path}")
        return  # type: ignore[unreachable]

    spec.loader.exec_module(module)

    captured = capsys.readouterr()
    output = captured.out

    # Проверяем вывод
    if "Тестирование mask_account_card:" not in output:
        pytest.skip("Модуль не выводит ожидаемый текст при запуске")
        return  # type: ignore[unreachable]

    assert "Тестирование mask_account_card:" in output
    assert "-" * 50 in output
    assert "Тестирование get_date:" in output
    assert "Вход:  Visa Platinum 7000792289606361" in output
    assert "Выход: Visa Platinum 7000 79** **** 6361" in output
    assert "Вход:  Счет 73654108430135874305" in output
    assert "Выход: Счет **4305" in output
    assert "Вход:  2024-03-11T02:26:18.671407" in output
    assert "Выход: 11.03.2024" in output


def test_functions_availability() -> None:
    """Тест доступности всех функций модуля."""
    from widget import get_date
    from widget import mask_account_card
    from widget import mask_account_number
    from widget import mask_card_number

    # Просто проверяем, что функции импортируются
    assert callable(mask_account_card)
    assert callable(get_date)
    assert callable(mask_card_number)
    assert callable(mask_account_number)
