"""Модуль утилит для работы с данными."""

import json
import logging
import os
from logging import FileHandler, Formatter
from pathlib import Path
from typing import Any, Dict, List

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

    try:
        # Проверяем существует ли файл
        if not os.path.exists(file_path):
            # Логирование включено в ошибочные случаи использования функций модуля utils
            # Логирование ошибочных случаев использования функций модуля utils производится с уровнем не ниже ERROR
            logger.error(f"Файл не найден: {file_path}")
            return []

        # Проверяем размер файла
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            logger.warning(f"Файл пустой: {file_path}")
            return []

        logger.debug(f"Размер файла: {file_size} байт")

        # Читаем и парсим JSON
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Проверяем, что data - это список
        if not isinstance(data, list):
            logger.error(f"Данные в файле не являются списком. Тип: {type(data)}")
            return []

        logger.info(f"Успешно загружено {len(data)} записей из файла: {file_path}")
        return data

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
