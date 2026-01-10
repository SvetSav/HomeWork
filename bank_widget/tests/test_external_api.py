"""
Тесты для модуля external_api.
"""

import os
import sys
from pathlib import Path
from typing import Iterator
from unittest.mock import Mock, patch
import pytest

# Добавляем путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Прямой импорт
from external_api import get_exchange_rate, convert_amount_to_rub  # noqa: E402


def test_get_exchange_rate_rub() -> None:
    """Тест получения курса для RUB (должен быть 1.0)."""
    result = get_exchange_rate("RUB")
    assert result == 1.0


@patch.dict(os.environ, {"EXCHANGE_RATE_API_KEY": "test_key"})
@patch('external_api.requests.get')
def test_get_exchange_rate_success(mock_get: Mock) -> None:
    """Тест успешного получения курса валют."""
    # Мокаем ответ API
    mock_response = Mock()
    mock_response.json.return_value = {
        "success": True,
        "rates": {"RUB": 75.5}
    }
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    result = get_exchange_rate("USD")

    assert result == 75.5
    mock_get.assert_called_once()
    assert "apikey" in mock_get.call_args[1]["headers"]


@patch.dict(os.environ, {"EXCHANGE_RATE_API_KEY": "test_key"})
@patch('external_api.requests.get')
def test_get_exchange_rate_api_error(mock_get: Mock) -> None:
    """Тест получения ошибки от API."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "success": False,
        "error": {"info": "Invalid API key"}
    }
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    result = get_exchange_rate("USD")

    assert result is None


@patch.dict(os.environ, {}, clear=True)
def test_get_exchange_rate_no_api_key() -> None:
    """Тест отсутствия API ключа в переменных окружения."""
    result = get_exchange_rate("USD")
    assert result is None


@patch('external_api.get_exchange_rate')
def test_convert_amount_to_rub_rub(mock_get_rate: Mock) -> None:
    """Тест конвертации RUB в RUB (без конвертации)."""
    transaction = {"amount": "100.50", "currency": "RUB"}

    result = convert_amount_to_rub(transaction)

    assert result == 100.50
    mock_get_rate.assert_not_called()


@patch('external_api.get_exchange_rate')
def test_convert_amount_to_rub_usd(mock_get_rate: Mock) -> None:
    """Тест конвертации USD в RUB."""
    transaction = {"amount": "100.00", "currency": "USD"}
    mock_get_rate.return_value = 75.5

    result = convert_amount_to_rub(transaction)

    assert result == 7550.0
    mock_get_rate.assert_called_once_with("USD")


@patch('external_api.get_exchange_rate')
def test_convert_amount_to_rub_eur(mock_get_rate: Mock) -> None:
    """Тест конвертации EUR в RUB."""
    transaction = {"amount": "50.00", "currency": "EUR"}
    mock_get_rate.return_value = 85.25

    result = convert_amount_to_rub(transaction)
    assert result == 4262.5
    mock_get_rate.assert_called_once_with("EUR")


@patch('external_api.get_exchange_rate')
def test_convert_amount_to_rub_api_failure(mock_get_rate: Mock) -> None:
    """Тест конвертации при ошибке API."""
    transaction = {"amount": "100.00", "currency": "USD"}
    mock_get_rate.return_value = None

    result = convert_amount_to_rub(transaction)
    assert result is None


def test_convert_amount_to_rub_no_amount() -> None:
    """Тест конвертации транзакции без суммы."""
    transaction = {"currency": "USD"}
    result = convert_amount_to_rub(transaction)
    assert result is None


def test_convert_amount_to_rub_invalid_amount() -> None:
    """Тест конвертации с невалидной суммой."""
    transaction = {"amount": "not_a_number", "currency": "USD"}
    result = convert_amount_to_rub(transaction)
    assert result is None


@patch('external_api.get_exchange_rate')
def test_convert_amount_to_rub_rounding(mock_get_rate: Mock) -> None:
    """Тест округления при конвертации."""
    transaction = {"amount": "100.123", "currency": "USD"}
    mock_get_rate.return_value = 75.5555

    result = convert_amount_to_rub(transaction)

    # 100.123 * 75.5555 = 7564.8433265 округляем до 7564.84
    assert result == 7564.84


@pytest.fixture
def mock_exchange_rate() -> Iterator[Mock]:
    """Фикстура для мока get_exchange_rate."""
    with patch('external_api.get_exchange_rate') as mock:  # Измените здесь
        yield mock


def test_convert_multiple_currencies(mock_exchange_rate: Mock) -> None:
    """Тест конвертации нескольких валют."""
    def side_effect(currency: str) -> float:
        rates = {"USD": 75.5, "EUR": 85.25, "GBP": 95.0}
        return rates.get(currency, 1.0)

    mock_exchange_rate.side_effect = side_effect

    transactions = [
        {"amount": "100", "currency": "USD"},
        {"amount": "50", "currency": "EUR"},
        {"amount": "30", "currency": "GBP"},
        {"amount": "200", "currency": "RUB"}
    ]

    expected_results = [7550.0, 4262.5, 2850.0, 200.0]

    for trans, expected in zip(transactions, expected_results):
        result = convert_amount_to_rub(trans)
        assert result == expected
