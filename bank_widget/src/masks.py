"""Модуль для маскировки номеров банковских карт и счетов."""

import logging
from logging import FileHandler
from logging import Formatter
from pathlib import Path

# Создаем логгер для модуля masks
logger = logging.getLogger('bank_widget.masks')
logger.setLevel(logging.DEBUG)

# Убедимся, что у логгера нет обработчиков (чтобы не добавлять дубликаты)
if not logger.handlers:
    # Создаем путь к файлу логов в корне проекта (папка logs)
    # Предполагаем, что структура: project_root/logs/masks.log
    # где project_root содержит папки src/, tests/, logs/ и т.д.
    current_dir = Path(__file__).parent  # src/
    project_root = current_dir.parent    # project_root/
    log_dir = project_root / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'masks.log'

    # Настраиваем file_handler для логера модуля masks
    file_handler = FileHandler(log_file, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # Настраиваем file_formatter для логера модуля masks
    formatter = Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Формат записи логов включает метку времени, название модуля, уровень серьезности и сообщение
    file_handler.setFormatter(formatter)

    # Установлен форматер для логера модуля masks
    # Добавлен handler для логера модуля masks
    logger.addHandler(file_handler)


def get_mask_card_number(card_number: int) -> str:
    """Замаскируйте номер банковской карты по шаблону XXXX XX****** XXXX."""
    # Логирование включено в успешные случаи использования функций модуля masks
    logger.info(f"Запрос на маскировку номера карты: {card_number}")

    card_str = str(card_number)

    if len(card_str) != 16:
        # Логирование включено в ошибочные случаи использования функций модуля masks
        # Логирование ошибочных случаев использования функций модуля masks производится с уровнем не ниже ERROR
        error_msg = "Номер карты должен состоять из 16 цифр."
        logger.error(f"{error_msg} Получено: {card_number} (длина: {len(card_str)})")
        raise ValueError(error_msg)

    masked = f"{card_str[:4]} {card_str[4:6]}** **** {card_str[-4:]}"
    logger.info(f"Номер карты замаскирован: {masked}")
    return masked


def get_mask_account(account_number: int) -> str:
    """Замаскируйте номер банковского счета в соответствии с шаблоном **XXXX."""
    # Логирование включено в успешные случаи использования функций модуля masks
    logger.info(f"Запрос на маскировку номера счета: {account_number}")

    account_str = str(account_number)

    if len(account_str) < 4:
        # Логирование включено в ошибочные случаи использования функций модуля masks
        # Логирование ошибочных случаев использования функций модуля masks производится с уровнем не ниже ERROR
        error_msg = "Длина номера счета должна составлять не менее 4 цифр."
        logger.error(f"{error_msg} Получено: {account_number} (длина: {len(account_str)})")
        raise ValueError(error_msg)

    masked = f"**{account_str[-4:]}"
    logger.info(f"Номер счета замаскирован: {masked}")
    return masked
