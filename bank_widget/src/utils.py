"""Модуль утилит для работы с данными."""

import json
import logging
import os
from logging import FileHandler
from logging import Formatter
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List

# Создаем логгер для модуля utils
logger = logging.getLogger('bank_widget.utils')
logger.setLevel(logging.DEBUG)

# Убедимся, что у логгера нет обработчиков (чтобы не добавлять дубликаты)
if not logger.handlers:
    # Создаем путь к файлу логов в корне проекта (папка logs)
    # Предполагаем, что структура: project_root/logs/utils.log
    # где project_root содержит папки src/, tests/, logs/ и т.д.
    current_dir = Path(__file__).parent  # src/
    project_root = current_dir.parent  # project_root/
    log_dir = project_root / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'utils.log'

    # Настраиваем file_handler для логера модуля utils
    file_handler = FileHandler(log_file, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # Настраиваем file_formatter для логера модуля utils
    formatter = Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Формат записи логов включает метку времени, название модуля, уровень серьезности и сообщение
    file_handler.setFormatter(formatter)

    # Установлен форматер для логера модуля utils
    # Добавлен handler для логера модуля utils
    logger.addHandler(file_handler)


def load_json_data(file_path: str) -> List[Dict[str, Any]]:
    """
    Загружает данные из JSON файла и возвращает список словарей.
    """
    # Логирование включено в успешные случаи использования функций модуля utils
    logger.info(f"Начало загрузки данных из файла: {file_path}")

    # Проверяем существует ли файл ДО try-except блока
    if not os.path.exists(file_path):
        logger.error(f"Файл не найден: {file_path}")
        return []

    # Проверяем размер файла ДО try-except блока
    file_size = os.path.getsize(file_path)
    if file_size == 0:
        logger.warning(f"Файл пустой: {file_path}")
        return []

    logger.debug(f"Размер файла: {file_size} байт")

    try:
        # Читаем и парсим JSON
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Проверяем, что data - это список
        if not isinstance(data, list):
            logger.error(f"Данные в файле не являются списком. Тип: {type(data)}")
            return []

        # Нормализуем данные
        normalized_data = normalize_transaction_data(data)

        logger.info(f"Успешно загружено {len(normalized_data)} записей из файла: {file_path}")
        return normalized_data

    except json.JSONDecodeError as e:
        logger.error(f"Ошибка декодирования JSON в файле {file_path}: {e}")
        return []
    except IOError as e:
        logger.error(f"Ошибка ввода/вывода при чтении файла {file_path}: {e}")
        return []
    except OSError as e:
        logger.error(f"Ошибка ОС при работе с файлом {file_path}: {e}")
        return []
    except Exception as e:
        logger.exception(f"Неожиданная ошибка при загрузке JSON файла {file_path}: {e}")
        return []


def normalize_transaction_data(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Нормализует данные транзакций, приводя их к единому формату.

    Args:
        transactions: Список транзакций в различных форматах

    Returns:
        Нормализованный список транзакций
    """
    logger.info(f"Нормализация данных транзакций (количество: {len(transactions)})")

    normalized = []

    for transaction in transactions:
        if not isinstance(transaction, dict):
            continue  # type: ignore[unreachable]

        normalized_transaction = {}

        # ID
        transaction_id = transaction.get('id')
        if transaction_id is not None:
            normalized_transaction['id'] = transaction_id

        # State (статус)
        state = transaction.get('state')
        if state:
            normalized_transaction['state'] = str(state).upper()

        # Date (дата)
        date = transaction.get('date')
        if date:
            normalized_transaction['date'] = str(date)

        # Description (описание)
        description = transaction.get('description')
        if description:
            normalized_transaction['description'] = str(description)

        # From (откуда)
        from_field = transaction.get('from')
        if from_field:
            normalized_transaction['from'] = str(from_field)

        # To (куда)
        to_field = transaction.get('to')
        if to_field:
            normalized_transaction['to'] = str(to_field)

        # Amount и Currency (сумма и валюта)
        # Обрабатываем разные форматы
        amount = None
        currency = None

        # Формат 1: operationAmount -> amount и operationAmount -> currency -> code/name
        operation_amount = transaction.get('operationAmount')
        if operation_amount and isinstance(operation_amount, dict):
            amount = operation_amount.get('amount')
            currency_data = operation_amount.get('currency', {})
            if isinstance(currency_data, dict):
                currency = currency_data.get('code') or currency_data.get('name')

        # Формат 2: отдельные поля amount и currency
        if not amount:
            amount = transaction.get('amount')
        if not currency:
            currency = transaction.get('currency')

        # Формат 3: вложенный currency
        if isinstance(currency, dict):
            currency = currency.get('code') or currency.get('name')

        if amount:
            normalized_transaction['amount'] = amount
        if currency:
            normalized_transaction['currency'] = currency

        normalized.append(normalized_transaction)

    logger.info(f"Нормализовано {len(normalized)} транзакций")
    return normalized


def get_available_statuses(transactions: List[Dict[str, Any]]) -> List[str]:
    """
    Возвращает список доступных статусов из транзакций.

    Args:
        transactions: Список транзакций

    Returns:
        Список уникальных статусов
    """
    statuses = set()

    for transaction in transactions:
        state = transaction.get('state')
        if state:
            statuses.add(str(state).upper())

    return sorted(list(statuses))


if __name__ == "__main__":
    # Тестирование функций
    print("Тестирование утилит:")
    print("=" * 50)

    # Тест normalize_transaction_data
    test_data = [
        {
            "id": 441945886,
            "state": "EXECUTED",
            "date": "2019-08-26T10:50:58.294041",
            "operationAmount": {
                "amount": "31957.58",
                "currency": {
                    "name": "руб.",
                    "code": "RUB"
                }
            },
            "description": "Перевод организации",
            "from": "Maestro 1596837868705199",
            "to": "Счет 64686473678894779589"
        },
        {
            "id": 41428829,
            "state": "executed",  # нижний регистр
            "date": "2019-07-03T18:35:29.512364",
            "amount": "8221.37",
            "currency": "USD",
            "description": "Перевод организации"
        }
    ]

    print("1. Нормализация данных:")
    normalized = normalize_transaction_data(test_data)
    for i, trans in enumerate(normalized, 1):
        print(f"\nТранзакция {i}:")
        print(f"  ID: {trans.get('id')}")
        print(f"  State: {trans.get('state')}")
        print(f"  Description: {trans.get('description')}")
        print(f"  Amount: {trans.get('amount')}")
        print(f"  Currency: {trans.get('currency')}")

    print("\n2. Получение доступных статусов:")
    statuses = get_available_statuses(normalized)
    print(f"  Доступные статусы: {statuses}")

    print("\nВсе функции работают корректно!")
