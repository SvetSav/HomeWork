"""
Тесты для модуля operations.
"""

import logging
import os
import re
import sys
from typing import Any
from typing import Dict
from typing import List
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from operations import count_transactions_by_category
from operations import filter_transactions_by_currency
from operations import format_transaction_for_display
from operations import search_transactions_by_description

# Добавляем путь к src перед импортами из src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestOperations:
    """Тесты модуля operations."""

    @pytest.fixture
    def sample_transactions(self) -> List[Dict[str, Any]]:
        """Фикстура с тестовыми транзакциями."""
        return [
            {
                "id": 1,
                "description": "Перевод организации",
                "date": "2024-01-01T00:00:00.000000",
                "from": "Visa Platinum 7000792289606361",
                "to": "Счет 73654108430135874305",
                "operationAmount": {
                    "amount": "100.50",
                    "currency": {"name": "руб.", "code": "RUB"}
                }
            },
            {
                "id": 2,
                "description": "Оплата услуг связи",
                "date": "2024-01-02T00:00:00.000000",
                "from": "MasterCard 7158300734726758",
                "to": "Счет 64686473678894779589",
                "operationAmount": {
                    "amount": "50.00",
                    "currency": {"name": "USD", "code": "USD"}
                }
            },
            {
                "id": 3,
                "description": "Перевод с карты на карту",
                "date": "2024-01-03T00:00:00.000000",
                "from": "Visa Classic 6831982476737658",
                "to": "Visa Platinum 8990922113665229",
                "operationAmount": {
                    "amount": "200.75",
                    "currency": {"name": "EUR", "code": "EUR"}
                }
            },
            {
                "id": 4,
                "description": "Перевод организации",
                "date": "2024-01-04T00:00:00.000000",
                "from": "Maestro 1596837868705199",
                "to": "Счет 35383033474447895560",
                "operationAmount": {
                    "amount": "300.00",
                    "currency": {"name": "руб.", "code": "RUB"}
                }
            },
        ]

    def test_search_transactions_by_description_exact_match(self, sample_transactions: List[Dict[str, Any]]) -> None:
        """Тест поиска транзакций по точному совпадению."""
        result = search_transactions_by_description(sample_transactions, "Перевод организации")

        assert len(result) == 2
        assert all("Перевод организации" in t["description"] for t in result)

    def test_search_transactions_by_description_partial_match(self, sample_transactions: List[Dict[str, Any]]) -> None:
        """Тест поиска транзакций по частичному совпадению."""
        result = search_transactions_by_description(sample_transactions, "Перевод")

        assert len(result) == 3
        assert all("Перевод" in t["description"] for t in result)

    def test_search_transactions_by_description_case_insensitive(self,
                                                                 sample_transactions: List[Dict[str, Any]]) -> None:
        """Тест поиска транзакций без учета регистра."""
        result = search_transactions_by_description(sample_transactions, "ОРГАНИЗАЦИИ")

        assert len(result) == 2
        assert all("организации" in t["description"].lower() for t in result)

    def test_search_transactions_by_description_empty_search(self, sample_transactions: List[Dict[str, Any]]) -> None:
        """Тест поиска с пустой строкой поиска."""
        result = search_transactions_by_description(sample_transactions, "")

        assert len(result) == len(sample_transactions)

    def test_search_transactions_by_description_empty_list(self) -> None:
        """Тест поиска с пустым списком транзакций."""
        result = search_transactions_by_description([], "Перевод")

        assert result == []

    @patch('re.compile')
    def test_search_transactions_by_description_regex_error(self, mock_compile: Mock,
                                                            sample_transactions: List[Dict[str, Any]]) -> None:
        """Тест поиска при ошибке в регулярном выражении."""
        mock_compile.side_effect = re.error("Invalid regex")

        result = search_transactions_by_description(sample_transactions, "Перевод")

        # Должен вернуться к простому поиску
        assert len(result) == 3

    def test_count_transactions_by_category_single_category(self, sample_transactions: List[Dict[str, Any]]) -> None:
        """Тест подсчета транзакций по одной категории."""
        result = count_transactions_by_category(sample_transactions, ["Перевод"])

        assert result == {"Перевод": 3}

    def test_count_transactions_by_category_multiple_categories(self,
                                                                sample_transactions: List[Dict[str, Any]]) -> None:
        """Тест подсчета транзакций по нескольким категориям."""
        result = count_transactions_by_category(sample_transactions, ["Перевод", "Оплата"])

        assert result == {"Перевод": 3, "Оплата": 1}

    def test_count_transactions_by_category_case_insensitive(self, sample_transactions: List[Dict[str, Any]]) -> None:
        """Тест подсчета транзакций без учета регистра."""
        result = count_transactions_by_category(sample_transactions, ["ОРГАНИЗАЦИИ", "УСЛУГ"])

        assert result == {"ОРГАНИЗАЦИИ": 2, "УСЛУГ": 1}

    def test_count_transactions_by_category_empty_list(self) -> None:
        """Тест подсчета с пустым списком транзакций."""
        result = count_transactions_by_category([], ["Перевод", "Оплата"])

        assert result == {"Перевод": 0, "Оплата": 0}

    def test_count_transactions_by_category_empty_categories(self, sample_transactions: List[Dict[str, Any]]) -> None:
        """Тест подсчета с пустым списком категорий."""
        result = count_transactions_by_category(sample_transactions, [])

        assert result == {}

    def test_filter_transactions_by_currency_rub(self, sample_transactions: List[Dict[str, Any]]) -> None:
        """Тест фильтрации транзакций по валюте RUB."""
        result = filter_transactions_by_currency(sample_transactions, "RUB")

        assert len(result) == 2
        assert all(t["operationAmount"]["currency"]["code"] == "RUB" for t in result)

    def test_filter_transactions_by_currency_usd(self, sample_transactions: List[Dict[str, Any]]) -> None:
        """Тест фильтрации транзакций по валюте USD."""
        result = filter_transactions_by_currency(sample_transactions, "USD")

        assert len(result) == 1
        assert result[0]["operationAmount"]["currency"]["code"] == "USD"

    def test_filter_transactions_by_currency_empty(self) -> None:
        """Тест фильтрации с пустым списком транзакций."""
        result = filter_transactions_by_currency([], "RUB")

        assert result == []

    def test_format_transaction_for_display(self, sample_transactions: List[Dict[str, Any]]) -> None:
        """Тест форматирования транзакции для вывода."""
        transaction = sample_transactions[0]
        result = format_transaction_for_display(transaction)

        assert "01.01.2024" in result
        assert "Перевод организации" in result
        assert "7000 79** **** 6361" in result or "Visa Platinum" in result
        assert "**4305" in result or "Счет" in result
        assert "100.50" in result
        assert "руб." in result

    def test_format_transaction_for_display_missing_fields(self) -> None:
        """Тест форматирования транзакции с отсутствующими полями."""
        transaction = {"id": 1, "description": "Тестовая транзакция"}
        result = format_transaction_for_display(transaction)

        assert "Тестовая транзакция" in result
        assert "Нет описания" not in result


def test_operations_logger_created() -> None:
    """Тест создания логгера для модуля operations."""
    from operations import logger  # Импорт внутри функции, чтобы избежать циклических зависимостей

    assert logger.name == "bank_widget.operations"
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) > 0
