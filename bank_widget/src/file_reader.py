"""
Модуль для чтения финансовых операций из CSV и Excel файлов.
"""

import logging
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
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


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Нормализует названия колонок DataFrame.

    Args:
        df: DataFrame для нормализации

    Returns:
        DataFrame с нормализованными названиями колонок
    """
    # Приводим названия колонок к нижнему регистру и удаляем пробелы
    df.columns = [str(col).strip().lower() for col in df.columns]

    # Маппинг русских названий на английские
    column_mapping = {
        'статус': 'state',
        'дата': 'date',
        'описание': 'description',
        'откуда': 'from',
        'куда': 'to',
        'сумма': 'amount',
        'валюта': 'currency',
        'id': 'id',
        'идентификатор': 'id'
    }

    # Переименовываем колонки
    df.rename(columns=column_mapping, inplace=True)

    return df


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

        # Пробуем разные кодировки
        encodings = ['utf-8', 'cp1251', 'windows-1251', 'latin1']

        for encoding in encodings:
            try:
                logger.debug(f"Попытка чтения с кодировкой {encoding}")
                df = pd.read_csv(file_path, encoding=encoding)

                # Нормализуем названия колонок
                df = normalize_column_names(df)

                logger.debug(f"CSV файл прочитан, размер: {df.shape}")

                if df.empty:
                    logger.warning(f"CSV файл пуст: {file_path}")
                    return []

                # Заменяем NaN на None
                df = df.where(pd.notnull(df), None)  # type: ignore[call-overload]

                # Конвертируем DataFrame в список словарей
                transactions_raw = df.to_dict('records')
                transactions = cast(List[Dict[str, Any]], transactions_raw)

                logger.info(f"Успешно прочитано {len(transactions)} транзакций из CSV файла: {file_path}")

                return transactions

            except UnicodeDecodeError:
                logger.debug(f"Кодировка {encoding} не подошла")
                continue
            except Exception as e:
                logger.debug(f"Ошибка при чтении с кодировкой {encoding}: {e}")
                continue

        # Если ни одна кодировка не подошла
        logger.error(f"Не удалось прочитать CSV файл ни с одной из кодировок: {file_path}")
        raise ValueError(f"Не удалось прочитать CSV файл: {file_path}")

    except pd.errors.EmptyDataError:
        logger.error(f"CSV файл пуст или не содержит данных: {file_path}")
        return []
    except pd.errors.ParserError as e:
        logger.error(f"Ошибка парсинга CSV файла {file_path}: {e}")
        # Попробуем читать с другими параметрами
        try:
            df = pd.read_csv(file_path, on_bad_lines='warn')
            df = normalize_column_names(df)
            if df.empty:
                return []
            df = df.where(pd.notnull(df), None)  # type: ignore[call-overload]
            transactions_raw = df.to_dict('records')
            transactions = cast(List[Dict[str, Any]], transactions_raw)
            logger.info(f"Прочитано {len(transactions)} транзакций (с пропуском ошибок)")
            return transactions
        except Exception as parse_error:
            logger.error(f"Не удалось прочитать CSV даже с пропуском ошибок: {parse_error}")
            raise ValueError(f"Ошибка формата CSV файла: {file_path}")
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

        # Нормализуем названия колонок
        df = normalize_column_names(df)

        logger.debug(f"Excel файл прочитан, размер: {df.shape}")

        if df.empty:
            logger.warning(f"Excel файл пуст: {file_path}")
            return []

        # Заменяем NaN на None
        df = df.where(pd.notnull(df), None)  # type: ignore[call-overload]

        # Конвертируем DataFrame в список словарей
        transactions_raw = df.to_dict('records')
        transactions = cast(List[Dict[str, Any]], transactions_raw)

        logger.info(f"Успешно прочитано {len(transactions)} транзакций из Excel файла: {file_path}")

        return transactions

    except pd.errors.EmptyDataError:
        logger.error(f"Excel файл пуст или не содержит данных: {file_path}")
        return []
    except ValueError as e:
        if "Worksheet" in str(e):
            logger.error(f"Лист '{sheet_name}' не найден в Excel файле {file_path}")
            # Пробуем прочитать все листы
            try:
                xls = pd.ExcelFile(file_path)
                sheet_names = xls.sheet_names
                logger.info(f"Доступные листы: {sheet_names}")
                if sheet_names:
                    df = pd.read_excel(file_path, sheet_name=sheet_names[0])
                    df = normalize_column_names(df)
                    if df.empty:
                        return []
                    df = df.where(pd.notnull(df), None)  # type: ignore[call-overload]
                    transactions_raw = df.to_dict('records')
                    transactions = cast(List[Dict[str, Any]], transactions_raw)
                    logger.info(f"Прочитано {len(transactions)} транзакций из первого листа '{sheet_names[0]}'")
                    return transactions
            except Exception as sheet_error:
                logger.debug(f"Не удалось прочитать первый лист: {sheet_error}")
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
    elif ext in ['.xlsx', '.xls', '.xlsm', '.xlsb']:
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
