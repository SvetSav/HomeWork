"""
Тесты для модуля utils.
"""

import json
import os
import tempfile
from typing import Any
from typing import Dict
from typing import List

import pytest
from utils import load_json_data


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
