"""
Фикстуры для тестирования.
"""
import os
import sys

# Добавляем src в путь Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


from typing import Any  # noqa: E402
from typing import Dict  # noqa: E402
from typing import List  # noqa: E402

import pytest  # noqa: E402


# Фикстуры для masks.py
@pytest.fixture
def valid_card_numbers() -> List[int]:
    """Корректные номера карт."""
    return [
        7000792289606361,
        1596837868705199,
        7158300734726758,
        6831982476737658,
    ]


@pytest.fixture
def valid_account_numbers() -> List[int]:
    """Корректные номера счетов."""
    return [
        73654108430135874305,
        64686473678894779589,
        35383033474447895560,
        1234,  # минимальная длина
    ]


# Фикстуры для widget.py
@pytest.fixture
def sample_cards() -> List[str]:
    """Тестовые карты."""
    return [
        "Visa Platinum 7000792289606361",
        "Maestro 1596837868705199",
        "MasterCard 7158300734726758",
        "Visa Classic 6831982476737658",
    ]


@pytest.fixture
def sample_accounts() -> List[str]:
    """Тестовые счета."""
    return [
        "Счет 73654108430135874305",
        "Счет 64686473678894779589",
        "Счет 35383033474447895560",
    ]


@pytest.fixture
def sample_dates() -> List[str]:
    """Тестовые даты."""
    return [
        "2024-03-11T02:26:18.671407",
        "2023-12-31T23:59:59.999999",
        "2024-01-01T00:00:00.000000",
    ]


# Фикстуры для processing.py
@pytest.fixture
def sample_operations() -> List[Dict[str, Any]]:
    """Тестовые операции."""
    return [
        {'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'},
        {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'},
        {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'},
        {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'},
        {'id': 123, 'state': 'PENDING', 'date': '2024-01-01T00:00:00.000000'},
        {'id': 456, 'state': 'EXECUTED', 'date': '2024-01-01T00:00:00.000000'},
    ]


@pytest.fixture
def operations_with_duplicate_dates() -> List[Dict[str, Any]]:
    """Операции с одинаковыми датами."""
    return [
        {'id': 1, 'state': 'EXECUTED', 'date': '2024-01-01T00:00:00.000000'},
        {'id': 2, 'state': 'EXECUTED', 'date': '2024-01-01T00:00:00.000000'},
        {'id': 3, 'state': 'CANCELED', 'date': '2024-01-01T00:00:00.000000'},
    ]


@pytest.fixture
def operations_with_invalid_dates() -> List[Dict[str, Any]]:
    """Операции с некорректными датами."""
    return [
        {'id': 1, 'state': 'EXECUTED', 'date': 'invalid-date'},
        {'id': 2, 'state': 'EXECUTED', 'date': ''},
        {'id': 3, 'state': 'EXECUTED', 'date': '2024-13-01T00:00:00.000000'},
    ]


@pytest.fixture
def sample_transactions() -> List[Dict[str, Any]]:
    """Тестовые транзакции для модуля generators."""
    return [
        {
            "id": 939719570,
            "state": "EXECUTED",
            "date": "2018-06-30T02:08:58.425572",
            "operationAmount": {
                "amount": "9824.07",
                "currency": {"name": "USD", "code": "USD"}
            },
            "description": "Перевод организации",
            "from": "Счет 75106830613657916952",
            "to": "Счет 11776614605963066702"
        },
    ]
