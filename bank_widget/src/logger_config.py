"""
Конфигурация логгера для проекта.
"""

import logging
from logging import FileHandler, Formatter
from pathlib import Path
from typing import Optional


def setup_logger(
        name: str,
        log_file: Optional[str] = None,
        level: int = logging.INFO  # Изменено с DEBUG на INFO
) -> logging.Logger:
    """
    Настраивает и возвращает логгер.
    """
    # Создаем логгер
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Если у логгера уже есть обработчики, не добавляем новые
    if logger.handlers:
        return logger

    # Формат логов
    formatter = Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Обработчик для консоли (опционально)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Обработчик для файла (если указан)
    if log_file:
        # Создаем директорию для логов, если ее нет
        log_dir = Path(log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)

        # Обработчик с перезаписью файла при каждом запуске
        file_handler = FileHandler(log_file, mode='w', encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_module_logger(module_name: str) -> logging.Logger:
    """
    Получает настроенный логгер для модуля.
    """
    # Создаем путь к файлу логов в папке logs
    # определяем корень проекта
    current_dir = Path(__file__).parent  # src/
    project_root = current_dir.parent    # project_root/
    log_file = project_root / 'logs' / f'{module_name}.log'

    # Используем имя модуля как имя логгера
    logger_name = f'bank_widget.{module_name}'

    return setup_logger(
        name=logger_name,
        log_file=str(log_file),
        level=logging.INFO  # Уровень INFO как в тестах
    )


# Логгеры для тестов и других модулей
masks_logger = get_module_logger('masks')
utils_logger = get_module_logger('utils')
