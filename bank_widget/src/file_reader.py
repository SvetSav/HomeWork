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

import pandas as pd

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
        'идентификатор': 'id',
        'operationamount': 'amount',  # Для JSON данных
        'operationamount.amount': 'amount',
        'operationamount.currency': 'currency',
        'operationamount.currency.name': 'currency',
        'operationamount.currency.code': 'currency_code'  # Оставляем отдельно
    }

    # Удаляем дублирующиеся колонки перед переименованием
    # Создаем словарь для отслеживания уникальных колонок
    unique_columns = {}
    columns_to_rename = {}

    for old_name in df.columns:
        # Определяем новое имя
        new_name = column_mapping.get(old_name, old_name)

        # Если новое имя уже существует, добавляем суффикс
        if new_name in unique_columns:
            suffix = 1
            while f"{new_name}_{suffix}" in unique_columns:
                suffix += 1
            new_name = f"{new_name}_{suffix}"

        unique_columns[new_name] = True
        columns_to_rename[old_name] = new_name

    # Переименовываем колонки
    df.rename(columns=columns_to_rename, inplace=True)

    logger.debug(f"Колонки после переименования: {df.columns.tolist()}")

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

        # Пробуем разные кодировки с разделителем ';'
        encodings = ['utf-8', 'cp1251', 'windows-1251', 'latin1']

        for encoding in encodings:
            try:
                logger.debug(f"Попытка чтения с кодировкой {encoding}, разделитель ';'")
                df = pd.read_csv(file_path, encoding=encoding, delimiter=';')

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

                # Полный словарь маппинга локализованных названий на коды валют
                currency_name_to_code = {
                    'Sol': 'PEN', 'Peso': 'COP', 'Shilling': 'TZS', 'Rupiah': 'IDR',
                    'Yuan Renminbi': 'CNY', 'Hryvnia': 'UAH', 'Koruna': 'CZK',
                    'Euro': 'EUR', 'Ruble': 'RUB', 'Krona': 'SEK', 'Yen': 'JPY',
                    'Zloty': 'PLN', 'Dollar': 'USD', 'Real': 'BRL', 'Dinar': 'TND',
                    'Franc': 'XAF', 'Quetzal': 'GTQ', 'Baht': 'THB', 'Ariary': 'MGA',
                    'Rial': 'QAR', 'Krone': 'NOK', 'Ringgit': 'MYR', 'Pula': 'BWP',
                    'Tenge': 'KZT', 'Won': 'KPW', 'Guilder': 'ANG', 'Shekel': 'ILS',
                    'Dram': 'AMD', 'Dong': 'VND', 'Dirham': 'MAD', 'Lek': 'ALL',
                    'Dalasi': 'GMD', 'Kwanza': 'AOA', 'Guarani': 'PYG', 'Birr': 'ETB',
                    'Kwacha': 'ZMW', 'Denar': 'MKD', 'Colon': 'CRC', 'Lempira': 'HNL',
                    'Tugrik': 'MNT', 'Kyat': 'MMK', 'Balboa': 'PAB', 'Gourde': 'HTG',
                    'Riels': 'KHR', 'Bolivar': 'VEF', 'Litas': 'LTL', 'Cordoba': 'NIO',
                    'Rupee': 'PKR', 'Rand': 'ZAR', 'Leu': 'MDL', 'Lilangeni': 'SZL',
                    'Forint': 'HUF', 'Kip': 'LAK', 'Cedi': 'GHS', 'Somoni': 'TJS',
                    'Ngultrum': 'BTN', 'Som': 'KGS', 'Boliviano': 'BOB', 'Manat': 'AZN',
                    'Marka': 'BAM', 'Lari': 'GEL', 'Tala': 'WST', 'Afghani': 'AFN', 'Kuna': 'HRK',
                    'Lev': 'BGN', 'руб.': 'RUB', 'рубль': 'RUB', '₽': 'RUB',
                    '$': 'USD', '€': 'EUR', '£': 'GBP', '¥': 'JPY'
                }

                # Дополнительные уточнения для неоднозначных названий
                # Если нужно различать песо разных стран, можно использовать контекст
                # или дополнительные данные, но здесь просто оставляем COP как наиболее частый

                for transaction in transactions:
                    # УНИФИЦИРОВАННАЯ ОБРАБОТКА ВАЛЮТЫ:
                    # 1. Если есть currency_code (код валюты), используем его - это уже унифицировано
                    if 'currency_code' in transaction and transaction['currency_code']:
                        transaction['currency'] = str(transaction['currency_code']).strip()

                    # 2. Если нет currency_code, но есть currency_name (локализованное название)
                    elif 'currency_name' in transaction and transaction['currency_name']:
                        # Получаем локализованное название
                        localized_name = str(transaction['currency_name']).strip()

                        # Ищем в маппинге
                        if localized_name in currency_name_to_code:
                            transaction['currency'] = currency_name_to_code[localized_name]
                        else:
                            # Если не нашли, оставляем как есть, но логируем предупреждение
                            transaction['currency'] = localized_name
                            logger.warning(f"Неизвестная валюта: {localized_name}")

                    # 3. Если есть currency, но это может быть локализованное название
                    elif 'currency' in transaction and transaction['currency']:
                        currency_str = str(transaction['currency']).strip()

                        # Проверяем, не является ли это уже кодом валюты (3 буквы)
                        if len(currency_str) == 3 and currency_str.isalpha() and currency_str.isupper():
                            # Это уже код, оставляем как есть
                            transaction['currency'] = currency_str
                        elif currency_str in currency_name_to_code:
                            # Это локализованное название, преобразуем в код
                            transaction['currency'] = currency_name_to_code[currency_str]
                        else:
                            # Неизвестно что, оставляем как есть
                            transaction['currency'] = currency_str

                    # 4. Если ничего нет, используем 'RUB' по умолчанию
                    else:
                        transaction['currency'] = 'RUB'  # Российский рубль по умолчанию

                    # Удаляем временные поля, если они есть
                    for field in ['currency_name', 'currency_code']:
                        if field in transaction:
                            del transaction[field]

                    # Также форматируем суммы если нужно
                    if 'amount' in transaction and transaction['amount'] is not None:
                        try:
                            amount_str = str(transaction['amount'])
                            amount_str = amount_str.replace(',', '.')
                            amount_num = float(amount_str)
                            if amount_num.is_integer():
                                transaction['amount'] = int(amount_num)
                            else:
                                transaction['amount'] = amount_num
                        except (ValueError, TypeError) as e:
                            logger.debug(f"Не удалось преобразовать сумму {transaction.get('amount')}: {e}")
                            pass

                logger.info(f"Успешно прочитано {len(transactions)} транзакций из CSV файла: {file_path}")
                return transactions

            except UnicodeDecodeError:
                logger.debug(f"Кодировка {encoding} не подошла")
                continue
            except pd.errors.EmptyDataError:
                logger.warning(f"CSV файл полностью пуст: {file_path}")
                return []
            except Exception as e:
                logger.debug(f"Ошибка при чтении с кодировкой {encoding}: {e}")
                continue

        # Если ни одна кодировка с разделителем ';' не подошла, пробуем без разделителя
        try:
            logger.debug("Попытка чтения без указания разделителя")
            df = pd.read_csv(file_path, encoding='utf-8')
            df = normalize_column_names(df)

            if df.empty:
                logger.warning(f"CSV файл пуст: {file_path}")
                return []

            df = df.fillna(pd.NA)
            transactions_raw = df.to_dict('records')
            transactions = cast(List[Dict[str, Any]], transactions_raw)

            # Та же обработка валюты с полным словарем
            currency_name_to_code = {
                'Sol': 'PEN', 'Peso': 'COP', 'Shilling': 'TZS', 'Rupiah': 'IDR',
                'Yuan Renminbi': 'CNY', 'Hryvnia': 'UAH', 'Koruna': 'CZK',
                'Euro': 'EUR', 'Ruble': 'RUB', 'Krona': 'SEK', 'Yen': 'JPY',
                'Zloty': 'PLN', 'Dollar': 'USD', 'Real': 'BRL', 'Dinar': 'TND',
                'Franc': 'XAF', 'Quetzal': 'GTQ', 'Baht': 'THB', 'Ariary': 'MGA',
                'Rial': 'QAR', 'Krone': 'NOK', 'Won': 'KRW', 'Afghani': 'AFN',
                'Ringgit': 'MYR', 'Pula': 'BWP', 'Tenge': 'KZT',
                'Guilder': 'ANG', 'Shekel': 'ILS', 'Dram': 'AMD', 'Dong': 'VND',
                'Dirham': 'MAD', 'Lek': 'ALL', 'Dalasi': 'GMD', 'Kwanza': 'AOA',
                'Guarani': 'PYG', 'Birr': 'ETB', 'Kwacha': 'ZMW', 'Denar': 'MKD',
                'Colon': 'CRC', 'Lempira': 'HNL', 'Tugrik': 'MNT', 'Kyat': 'MMK',
                'Balboa': 'PAB', 'Gourde': 'HTG', 'Riels': 'KHR', 'Bolivar': 'VEF',
                'Litas': 'LTL', 'Cordoba': 'NIO', 'Rupee': 'PKR', 'Rand': 'ZAR',
                'Leu': 'MDL', 'Lilangeni': 'SZL', 'Forint': 'HUF', 'Kip': 'LAK',
                'Cedi': 'GHS', 'Somoni': 'TJS', 'Ngultrum': 'BTN', 'Som': 'KGS',
                'Boliviano': 'BOB', 'Manat': 'AZN', 'Marka': 'BAM',
                'Lari': 'GEL', 'Tala': 'WST', 'Kuna': 'HRK', 'Lev': 'BGN', 'руб.': 'RUB'
            }

            for transaction in transactions:
                if 'currency_code' in transaction and transaction['currency_code']:
                    transaction['currency'] = str(transaction['currency_code']).strip()
                elif 'currency_name' in transaction and transaction['currency_name']:
                    localized_name = str(transaction['currency_name']).strip()
                    if localized_name in currency_name_to_code:
                        transaction['currency'] = currency_name_to_code[localized_name]
                    else:
                        transaction['currency'] = localized_name
                        logger.warning(f"Неизвестная валюта: {localized_name}")
                elif 'currency' in transaction and transaction['currency']:
                    currency_str = str(transaction['currency']).strip()
                    if len(currency_str) == 3 and currency_str.isalpha() and currency_str.isupper():
                        transaction['currency'] = currency_str
                    elif currency_str in currency_name_to_code:
                        transaction['currency'] = currency_name_to_code[currency_str]
                    else:
                        transaction['currency'] = currency_str
                else:
                    transaction['currency'] = 'RUB'

                for field in ['currency_name', 'currency_code']:
                    if field in transaction:
                        del transaction[field]

                if 'amount' in transaction and transaction['amount'] is not None:
                    try:
                        amount_str = str(transaction['amount'])
                        amount_str = amount_str.replace(',', '.')
                        amount_num = float(amount_str)
                        if amount_num.is_integer():
                            transaction['amount'] = int(amount_num)
                        else:
                            transaction['amount'] = amount_num
                    except (ValueError, TypeError):
                        pass

            logger.info(f"Прочитано {len(transactions)} транзакций из CSV файла (без разделителя): {file_path}")
            return transactions

        except pd.errors.EmptyDataError:
            logger.warning(f"CSV файл полностью пуст (без разделителя): {file_path}")
            return []
        except Exception as fallback_error:
            logger.error(
                f"Не удалось прочитать CSV файл ни с одной из кодировок: {file_path}, ошибка: {fallback_error}")
            raise ValueError(f"Не удалось прочитать CSV файл: {file_path}")

    except Exception as e:
        logger.error(f"Неожиданная ошибка при чтении CSV файла {file_path}: {e}")
        raise


def _read_csv_alternative(file_path: str) -> List[Dict[str, Any]]:
    """
    Альтернативный способ чтения CSV файла с использованием встроенного модуля csv.

    Args:
        file_path: Путь к CSV файлу

    Returns:
        Список словарей с транзакциями
    """
    import csv

    logger.info(f"Альтернативное чтение CSV файла: {file_path}")

    transactions = []
    encodings = ['utf-8', 'cp1251', 'windows-1251', 'latin1']

    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding, newline='') as csvfile:
                # Пробуем разные разделители
                for delimiter in [';', ',', '\t', '|']:
                    try:
                        csvfile.seek(0)  # Возвращаемся в начало файла
                        # Создаем reader с текущим разделителем
                        reader = csv.DictReader(csvfile, delimiter=delimiter)

                        # Читаем все строки
                        rows = list(reader)

                        if not rows:
                            logger.warning(f"CSV файл пуст (альтернативное чтение): {file_path}")
                            return []

                        # Нормализуем названия колонок в каждом ряду
                        normalized_rows: List[Dict[str, Any]] = []
                        for row in rows:
                            normalized_row: Dict[str, Optional[str]] = {}
                            for key, value in row.items():
                                normalized_key = key.strip().lower()
                                # Применяем маппинг как в normalize_column_names
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
                                if normalized_key in column_mapping:
                                    normalized_key = column_mapping[normalized_key]

                                # Обработка значений
                                if value is None or value == '':
                                    normalized_row[normalized_key] = None
                                else:
                                    normalized_row[normalized_key] = value.strip()

                            normalized_rows.append(normalized_row)

                        transactions = normalized_rows

                        # Добавляем валюту по умолчанию, если не указана
                        for transaction in transactions:
                            if 'currency' not in transaction or not transaction['currency']:
                                transaction['currency'] = 'руб.'

                            # Обработка суммы
                            if 'amount' in transaction and transaction['amount'] is not None:
                                try:
                                    amount_str = str(transaction['amount'])
                                    amount_str = amount_str.replace(',', '.')
                                    amount_num = float(amount_str)
                                    if amount_num.is_integer():
                                        transaction['amount'] = int(amount_num)
                                    else:
                                        transaction['amount'] = amount_num
                                except (ValueError, TypeError):
                                    pass

                        logger.info(f"Успешно прочитано {len(transactions)} транзакций альтернативным способом "
                                    f"(кодировка: {encoding}, разделитель: {delimiter})")
                        return transactions

                    except csv.Error as e:
                        logger.debug(f"Разделитель '{delimiter}' не подошел: {e}")
                        continue

        except UnicodeDecodeError:
            logger.debug(f"Кодировка {encoding} не подошла (альтернативное чтение)")
            continue
        except Exception as e:
            logger.debug(f"Ошибка при чтении с кодировкой {encoding} (альтернативное чтение): {e}")
            continue

    # Если ни одна комбинация не подошла
    raise ValueError(f"Не удалось прочитать CSV файл альтернативным способом: {file_path}")


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
        :rtype: List[Dict[str, Any]]
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

        # ОТЛАДКА: выводим колонки
        logger.debug(f"Колонки в Excel файле: {df.columns.tolist()}")
        if not df.empty:
            logger.debug(f"Первые строки:\n{df.head()}")

        if df.empty:
            logger.warning(f"Excel файл пуст: {file_path}")
            return []

        # Заменяем NaN на None
        df = df.where(pd.notnull(df), None)  # type: ignore[call-overload]

        # Конвертируем DataFrame в список словарей
        transactions_raw = df.to_dict('records')
        transactions = cast(List[Dict[str, Any]], transactions_raw)

        # ДОБАВЛЕНО: Обработка валюты для Excel файла
        for transaction in transactions:
            # Если currency отсутствует или None, устанавливаем значение по умолчанию
            if 'currency' not in transaction or transaction['currency'] is None:
                # Проверяем другие возможные поля с валютой
                if 'currency_code' in transaction and transaction['currency_code']:
                    transaction['currency'] = transaction['currency_code']
                elif 'currency_name' in transaction and transaction['currency_name']:
                    transaction['currency'] = transaction['currency_name']
                else:
                    # Значение по умолчанию
                    transaction['currency'] = 'RUB'

            # Удаляем временные поля
            for field in ['currency_name', 'currency_code']:
                if field in transaction:
                    del transaction[field]

            # Обработка суммы
            if 'amount' in transaction and transaction['amount'] is not None:
                try:
                    amount_str = str(transaction['amount'])
                    amount_str = amount_str.replace(',', '.')
                    amount_num = float(amount_str)
                    if amount_num.is_integer():
                        transaction['amount'] = int(amount_num)
                    else:
                        transaction['amount'] = amount_num
                except (ValueError, TypeError):
                    pass

        logger.info(f"Успешно прочитано {len(transactions)} транзакций из Excel файла: {file_path}")

        # ОТЛАДКА: выводим первую транзакцию
        if transactions:
            logger.debug(f"Первая транзакция после обработки: {transactions[0]}")

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

                    # Та же обработка валюты
                    for transaction in transactions:
                        if 'currency' not in transaction or transaction['currency'] is None:
                            if 'currency_code' in transaction and transaction['currency_code']:
                                transaction['currency'] = transaction['currency_code']
                            elif 'currency_name' in transaction and transaction['currency_name']:
                                transaction['currency'] = transaction['currency_name']
                            else:
                                transaction['currency'] = 'RUB'

                        for field in ['currency_name', 'currency_code']:
                            if field in transaction:
                                del transaction[field]

                        if 'amount' in transaction and transaction['amount'] is not None:
                            try:
                                amount_str = str(transaction['amount'])
                                amount_str = amount_str.replace(',', '.')
                                amount_num = float(amount_str)
                                if amount_num.is_integer():
                                    transaction['amount'] = int(amount_num)
                                else:
                                    transaction['amount'] = amount_num
                            except (ValueError, TypeError):
                                pass

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
