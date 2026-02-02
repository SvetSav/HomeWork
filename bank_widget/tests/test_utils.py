"""
Тесты для модуля utils.
"""

import json
import os
import tempfile
from typing import Any
from typing import Dict
from typing import List
from unittest.mock import patch

import pytest
from utils import get_available_statuses
from utils import load_json_data
from utils import logger
from utils import normalize_transaction_data


def test_load_json_data_valid() -> None:
    """Тест загрузки валидного JSON файла."""
    # Создаем временный файл с валидными данными
    data = [
        {"id": 1, "amount": 100, "currency": "RUB"},
        {"id": 2, "amount": 50, "currency": "USD"}
    ]

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(data, f)
        temp_path = f.name

    try:
        result = load_json_data(temp_path)
        assert result == data
        assert len(result) == 2
    finally:
        os.unlink(temp_path)


def test_load_json_data_empty_list() -> None:
    """Тест загрузки JSON файла с пустым списком."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump([], f)
        temp_path = f.name

    try:
        result = load_json_data(temp_path)
        assert result == []
    finally:
        os.unlink(temp_path)


def test_load_json_data_not_list() -> None:
    """Тест загрузки JSON файла, который не является списком."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"key": "value"}, f)  # dict вместо list
        temp_path = f.name

    try:
        result = load_json_data(temp_path)
        assert result == []
    finally:
        os.unlink(temp_path)


def test_load_json_data_file_not_found() -> None:
    """Тест загрузки несуществующего файла."""
    result = load_json_data("/nonexistent/path/file.json")
    assert result == []


def test_load_json_data_empty_file() -> None:
    """Тест загрузки пустого файла."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        # Пустой файл
        temp_path = f.name

    try:
        result = load_json_data(temp_path)
        assert result == []
    finally:
        os.unlink(temp_path)


def test_load_json_data_invalid_json() -> None:
    """Тест загрузки файла с невалидным JSON."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("{invalid json")
        temp_path = f.name

    try:
        result = load_json_data(temp_path)
        assert result == []
    finally:
        os.unlink(temp_path)


@pytest.fixture
def sample_transactions() -> List[Dict[str, Any]]:
    """Фикстура с тестовыми транзакциями."""
    return [
        {"id": 1, "amount": "100.50", "currency": "RUB", "description": "Покупка"},
        {"id": 2, "amount": "50.00", "currency": "USD", "description": "Онлайн-сервис"},
        {"id": 3, "amount": "30.75", "currency": "EUR", "description": "Подписка"}
    ]


def test_load_json_data_with_sample_data(sample_transactions: List[Dict[str, Any]]) -> None:
    """Тест загрузки файла с данными транзакций."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_transactions, f)
        temp_path = f.name

    try:
        result = load_json_data(temp_path)
        assert result == sample_transactions
        assert len(result) == 3
        assert result[0]["currency"] == "RUB"
        assert result[1]["currency"] == "USD"
    finally:
        os.unlink(temp_path)


def test_load_json_data_file_not_exists():
    non_existent_path = "/nonexistent/path/file.json"

    # Мокаем logger.error чтобы проверить вызов
    with patch.object(logger, 'error') as mock_error:
        result = load_json_data(non_existent_path)

        assert result == []
        # Проверяем что было залогировано
        mock_error.assert_called_once()
        assert "Файл не найден" in mock_error.call_args[0][0]


def test_load_json_data_json_decode_error():
    """Тест JSONDecodeError при чтении файла."""
    # Создаем файл с невалидным JSON
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("{invalid json")
        temp_path = f.name

    try:
        # Мокаем logger.error чтобы проверить вызов
        with patch.object(logger, 'error') as mock_error:
            result = load_json_data(temp_path)

            assert result == []
            # Проверяем что было залогировано
            mock_error.assert_called_once()
            assert "Ошибка декодирования JSON" in mock_error.call_args[0][0]

    finally:
        os.unlink(temp_path)


def test_load_json_data_io_error():
    """Тест IOError при чтении файла."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump([{"test": "data"}], f)
        temp_path = f.name

    try:
        # Мокаем open чтобы вызвать IOError
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            with patch.object(logger, 'error') as mock_error:
                result = load_json_data(temp_path)

                assert result == []
                # Проверяем что было залогировано
                mock_error.assert_called_once()
                assert "Ошибка ввода/вывода" in mock_error.call_args[0][0]

    finally:
        os.unlink(temp_path)


def test_load_json_data_general_exception():
    """Тест общее исключение при загрузке файла."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump([{"test": "data"}], f)
        temp_path = f.name

    try:
        # Мокаем json.load чтобы вызвать общее исключение
        with patch('json.load', side_effect=Exception("Unexpected error")):
            with patch.object(logger, 'exception') as mock_exception:
                result = load_json_data(temp_path)

                assert result == []
                # Проверяем что было залогировано
                mock_exception.assert_called_once()
                assert "Неожиданная ошибка" in mock_exception.call_args[0][0]

    finally:
        os.unlink(temp_path)


def test_normalize_transaction_data_empty_list():
    """Тест нормализация пустого списка транзакций."""
    # Мокаем logger.info чтобы проверить вызов
    with patch.object(logger, 'info') as mock_info:
        result = normalize_transaction_data([])

        assert result == []
        # Проверяем логирование
        assert mock_info.call_count >= 1
        # Первый вызов - начало нормализации
        assert "Нормализация данных транзакций" in mock_info.call_args_list[0][0][0]


def test_normalize_transaction_data_not_dict():
    """Тест транзакция не является словарем."""
    transactions = [
        {"id": 1, "amount": 100},  # валидная
        "not a dict",  # строка вместо словаря
        123,  # число вместо словаря
        None,  # None
        [],  # список
        {"id": 2, "amount": 200},  # валидная
    ]

    result = normalize_transaction_data(transactions)

    # Только валидные словари должны быть обработаны
    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[1]["id"] == 2


def test_normalize_transaction_data_field_processing():
    """Тест обработка различных полей."""
    transactions = [
        {
            "id": 123,
            "state": "executed",  # нижний регистр
            "date": "2024-01-01T12:00:00",
            "description": "Перевод",
            "from": "Счет 1234567890",
            "to": "Счет 0987654321",
            "amount": "1000.50",
            "currency": "RUB"
        },
        {
            "id": None,  # None значение
            "state": "",  # пустая строка
            "date": None,
            "description": 123,  # число вместо строки
            "from": True,  # boolean
            "to": 456.78,  # float
            "amount": 1000,  # число вместо строки
            "currency": {"code": "USD", "name": "Доллар"}
        },
        {
            # Нет обязательных полей
        },
        {
            "state": "CANCELED",  # верхний регистр
            "description": "",  # пустая строка
            "from": "   ",  # только пробелы
        },
    ]

    result = normalize_transaction_data(transactions)

    # Проверяем первую транзакцию
    assert result[0]["id"] == 123
    assert result[0]["state"] == "EXECUTED"  # преобразовано в верхний регистр
    assert result[0]["date"] == "2024-01-01T12:00:00"
    assert result[0]["description"] == "Перевод"
    assert result[0]["from"] == "Счет 1234567890"
    assert result[0]["to"] == "Счет 0987654321"
    assert result[0]["amount"] == "1000.50"
    assert result[0]["currency"] == "RUB"

    # Проверяем вторую транзакцию
    assert "id" not in result[1]  # None значение пропущено
    assert "state" not in result[1]  # пустая строка пропущена
    assert "date" not in result[1]  # None пропущено
    assert result[1]["description"] == "123"  # число преобразовано в строку
    assert result[1]["from"] == "True"  # boolean преобразован в строку
    assert result[1]["to"] == "456.78"  # float преобразован в строку
    assert result[1]["amount"] == 1000  # число как есть (не строка)
    assert result[1]["currency"] == "USD"  # code из словаря

    # Проверяем третью транзакцию
    assert result[2] == {}  # пустой словарь

    # Проверяем четвертую транзакцию
    assert result[3]["state"] == "CANCELED"
    assert "description" not in result[3]  # пустая строка пропущена
    assert result[3]["from"] == "   "  # строка с пробелами сохранена


def test_get_available_statuses_empty():
    """Тест get_available_statuses с пустым списком."""
    result = get_available_statuses([])
    assert result == []


def test_get_available_statuses_case_insensitive():
    """Тест get_available_statuses регистронезависимость."""
    transactions = [
        {"state": "executed"},
        {"state": "EXECUTED"},
        {"state": "ExEcUtEd"},
        {"state": "CancElEd"},
        {"state": "CANCELED"},
    ]

    result = get_available_statuses(transactions)

    # Дубликаты в разном регистре должны быть объединены
    assert len(result) == 2
    assert "EXECUTED" in result
    assert "CANCELED" in result


def test_load_json_data_not_list_normalization():
    """Тест когда JSON файл содержит не список, а нормализация все равно вызывается."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"key": "value"}, f)  # dict вместо list
        temp_path = f.name

    try:
        # Мокаем normalize_transaction_data чтобы проверить не вызывается ли она
        with patch('utils.normalize_transaction_data') as mock_normalize:
            with patch.object(logger, 'error') as mock_error:
                result = load_json_data(temp_path)

                assert result == []
                # Проверяем что была ошибка
                mock_error.assert_called_once()
                assert "не являются списком" in mock_error.call_args[0][0]
                # normalize_transaction_data не должна вызываться
                mock_normalize.assert_not_called()

    finally:
        os.unlink(temp_path)


def test_load_json_data_debug_logging():
    """Тест debug логирования размера файла."""
    data = [{"id": 1, "amount": 100}]

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(data, f)
        temp_path = f.name

    try:
        # Мокаем logger.debug чтобы проверить вызов
        with patch.object(logger, 'debug') as mock_debug:
            result = load_json_data(temp_path)

            assert len(result) == 1
            # Проверяем что было debug логирование
            mock_debug.assert_called_once()
            assert "Размер файла" in mock_debug.call_args[0][0]

    finally:
        os.unlink(temp_path)


def test_normalize_transaction_data_logging():
    """Тест логирования в normalize_transaction_data."""
    transactions = [{"id": 1}, {"id": 2}]

    # Мокаем logger.info чтобы проверить вызовы
    with patch.object(logger, 'info') as mock_info:
        result = normalize_transaction_data(transactions)

        assert len(result) == 2
        # Проверяем что было два info вызова
        assert mock_info.call_count >= 2
        # Первый вызов - начало нормализации
        assert "Нормализация данных транзакций" in mock_info.call_args_list[0][0][0]
        # Второй вызов - завершение нормализации
        assert "Нормализовано" in mock_info.call_args_list[1][0][0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
