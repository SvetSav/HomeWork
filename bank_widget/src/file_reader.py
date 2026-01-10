"""
Модуль для чтения финансовых операций из CSV и Excel файлов.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from typing import cast

import pandas as pd  # type: ignore

# Создаем логгер для модуля file_reader
logger = logging.getLogger('bank_widget.file_reader')
logger.setLevel(logging.DEBUG)

# Убедимся, что у логгера нет обработчиков
if not logger.handlers:
    # Создаем путь к файлу логов
    current_dir = Path(__file__).parent  # src/
    project_root = current_dir.parent    # project_root/
    log_dir = project_root / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'file_reader.log'

    # Настраиваем file_handler
    file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # Настраиваем formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def read_csv_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Считывает финансовые операции из CSV файла.

    Args:
        file_path: Путь к CSV файлу

    Returns:
        Список словарей с транзакциями

    Raises:
        FileNotFoundError: Если файл не найден
        ValueError: Если файл пуст или имеет неверный формат
    """
    logger.info(f"Начало чтения CSV файла: {file_path}")

    try:
        # Проверяем существование файла
        if not Path(file_path).exists():
            logger.error(f"CSV файл не найден: {file_path}")
            raise FileNotFoundError(f"Файл не найден: {file_path}")

        # Читаем CSV файл
        df = pd.read_csv(file_path, encoding='utf-8')
        logger.debug(f"CSV файл прочитан, размер: {df.shape}")

        if df.empty:
            logger.warning(f"CSV файл пуст: {file_path}")
            return []

        # Конвертируем DataFrame в список словарей
        # to_dict('records') возвращает List[Dict[Hashable, Any]], нужно преобразовать
        transactions_raw = df.to_dict('records')
        transactions = cast(List[Dict[str, Any]], transactions_raw)

        logger.info(f"Успешно прочитано {len(transactions)} транзакций из CSV файла: {file_path}")

        return transactions

    except pd.errors.EmptyDataError:
        logger.error(f"CSV файл пуст или не содержит данных: {file_path}")
        raise ValueError(f"Файл пуст или не содержит данных: {file_path}")
    except pd.errors.ParserError as e:
        logger.error(f"Ошибка парсинга CSV файла {file_path}: {e}")
        raise ValueError(f"Ошибка формата CSV файла: {file_path}")
    except UnicodeDecodeError:
        # Пробуем другую кодировку
        logger.debug(f"Попытка чтения CSV с кодировкой cp1251: {file_path}")
        try:
            df = pd.read_csv(file_path, encoding='cp1251')
            if df.empty:
                return []

            transactions_raw = df.to_dict('records')
            transactions = cast(List[Dict[str, Any]], transactions_raw)

            logger.info(f"Успешно прочитано {len(transactions)} транзакций из CSV (cp1251): {file_path}")
            return transactions
        except Exception as e:
            logger.error(f"Ошибка чтения CSV файла {file_path} с кодировкой cp1251: {e}")
            raise ValueError(f"Не удалось прочитать CSV файл: {file_path}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка при чтении CSV файла {file_path}: {e}")
        raise


def read_excel_file(file_path: str, sheet_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Считывает финансовые операции из Excel файла.

    Args:
        file_path: Путь к Excel файлу
        sheet_name: Название листа (если None, читается первый лист)

    Returns:
        Список словарей с транзакциями

    Raises:
        FileNotFoundError: Если файл не найден
        ValueError: Если файл пуст или имеет неверный формат
    """
    logger.info(f"Начало чтения Excel файла: {file_path} (лист: {sheet_name})")

    try:
        # Проверяем существование файла
        if not Path(file_path).exists():
            logger.error(f"Excel файл не найден: {file_path}")
            raise FileNotFoundError(f"Файл не найден: {file_path}")

        # Читаем Excel файл
        if sheet_name:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
        else:
            df = pd.read_excel(file_path)

        logger.debug(f"Excel файл прочитан, размер: {df.shape}")

        if df.empty:
            logger.warning(f"Excel файл пуст: {file_path}")
            return []

        # Конвертируем DataFrame в список словарей
        transactions_raw = df.to_dict('records')
        transactions = cast(List[Dict[str, Any]], transactions_raw)

        logger.info(f"Успешно прочитано {len(transactions)} транзакций из Excel файла: {file_path}")

        return transactions

    except pd.errors.EmptyDataError:
        logger.error(f"Excel файл пуст или не содержит данных: {file_path}")
        raise ValueError(f"Файл пуст или не содержит данных: {file_path}")
    except ValueError as e:
        if "Worksheet" in str(e):
            logger.error(f"Лист '{sheet_name}' не найден в Excel файле {file_path}")
            raise ValueError(f"Лист '{sheet_name}' не найден в файле: {file_path}")
        else:
            logger.error(f"Ошибка чтения Excel файла {file_path}: {e}")
            raise
    except Exception as e:
        logger.error(f"Неожиданная ошибка при чтении Excel файла {file_path}: {e}")
        raise


def detect_file_type(file_path: str) -> str:
    """
    Определяет тип файла по расширению.

    Args:
        file_path: Путь к файлу

    Returns:
        'csv', 'excel', 'json' или 'unknown'
    """
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext == '.csv':
        return 'csv'
    elif ext in ['.xlsx', '.xls']:
        return 'excel'
    elif ext == '.json':
        return 'json'
    else:
        return 'unknown'


def read_financial_data(file_path: str, **kwargs: Any) -> List[Dict[str, Any]]:
    """
    Универсальная функция для чтения финансовых данных из разных форматов.

    Args:
        file_path: Путь к файлу
        **kwargs: Дополнительные параметры (например, sheet_name для Excel)

    Returns:
        Список словарей с транзакциями

    Raises:
        ValueError: Если формат файла не поддерживается
    """
    logger.info(f"Чтение финансовых данных из файла: {file_path}")

    file_type = detect_file_type(file_path)

    if file_type == 'csv':
        return read_csv_file(file_path)
    elif file_type == 'excel':
        sheet_name = kwargs.get('sheet_name')
        return read_excel_file(file_path, sheet_name)
    elif file_type == 'json':
        # Используем существующую функцию из utils.py
        from .utils import load_json_data
        return load_json_data(file_path)
    else:
        logger.error(f"Неподдерживаемый формат файла: {file_path}")
        raise ValueError(f"Неподдерживаемый формат файла: {file_path}")
