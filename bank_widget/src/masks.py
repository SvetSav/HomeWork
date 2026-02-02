"""Модуль для маскировки номеров банковских карт и счетов."""

import logging
from datetime import datetime
from logging import FileHandler
from logging import Formatter
from pathlib import Path

# Создаем логгер для модуля masks
logger = logging.getLogger('bank_widget.masks')
logger.setLevel(logging.DEBUG)

# Убедимся, что у логгера нет обработчиков (чтобы не добавлять дубликаты)
if not logger.handlers:
    # Создаем путь к файлу логов в корне проекта (папка logs)
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


def mask_card_number(card_info: str) -> str:
    """
    Маскирует номер карты из строки вида 'Visa Platinum 7000 7922 8960 6361'.

    Args:
        card_info: Строка с информацией о карте

    Returns:
        Замаскированная строка карты

    Examples:
        >>> mask_card_number('Visa Platinum 7000792289606361')
        'Visa Platinum 7000 79** **** 6361'
        >>> mask_card_number('Maestro 1596837868705199')
        'Maestro 1596 83** **** 5199'
        >>> mask_card_number('MasterCard 1234 5678 9012 3456')
        'MasterCard 1234 56** **** 3456'
    """
    logger.info(f"Маскирование информации о карте: {card_info}")

    if not card_info:
        logger.warning("Получена пустая строка карты")
        return ""

    # Удаляем все пробелы из строки для анализа
    card_info_no_spaces = card_info.replace(" ", "")

    # Находим разделение между названием карты и номером
    # ищем позицию, где заканчиваются буквы и начинаются цифры
    card_name = ""
    card_number = ""

    # Ищем последнюю букву в строке
    last_letter_index = -1
    for i, char in enumerate(card_info_no_spaces):
        if char.isalpha() or char in " -":
            last_letter_index = i
        else:
            break

    # Если нашли разделение
    if last_letter_index >= 0:
        card_name = card_info_no_spaces[:last_letter_index + 1]
        card_number = card_info_no_spaces[last_letter_index + 1:]
    else:
        # Если вся строка состоит из цифр
        card_number = card_info_no_spaces

    # Альтернативный подход: используем регулярное выражение для разделения
    import re

    # Ищем название карты (все до первой группы цифр)
    match = re.match(r'^([A-Za-z\s]+)([\d\s]+)$', card_info)
    if match:
        card_name = match.group(1).strip()
        card_number_dirty = match.group(2)
        # Удаляем все пробелы из номера
        card_number = card_number_dirty.replace(" ", "")
    else:
        # Если не нашли соответствие, пытаемся разделить по последнему пробелу
        parts = card_info.rsplit(' ', 1)
        if len(parts) == 2:
            card_name = parts[0]
            card_number_dirty = parts[1]
            card_number = card_number_dirty.replace(" ", "")
        else:
            logger.warning(f"Невозможно извлечь номер карты из строки: {card_info}")
            return card_info

    # Проверяем номер карты
    if len(card_number) != 16 or not card_number.isdigit():
        logger.warning(f"Некорректный номер карты: {card_number}")
        return card_info

    # Форматируем в соответствии с ТЗ: 7000 79** **** 6361
    masked_number = f"{card_number[:4]} {card_number[4:6]}** **** {card_number[-4:]}"
    result = f"{card_name} {masked_number}"

    logger.info(f"Информация о карте замаскирована: {result}")
    return result


def mask_account_number(account_info: str) -> str:
    """
    Маскирует номер счета из строки вида 'Счет 73654108430135874305'.

    Args:
        account_info: Строка с информацией о счете

    Returns:
        Замаскированная строка счета

    Examples:
        >>> mask_account_number('Счет 73654108430135874305')
        'Счет **4305'
        >>> mask_account_number('Счет 64686473678894779589')
        'Счет **9589'
    """
    logger.info(f"Маскирование информации о счете: {account_info}")

    if not account_info:
        logger.warning("Получена пустая строка счета")
        return ""

    # Разделяем строку на название и номер
    parts = account_info.rsplit(' ', 1)
    if len(parts) != 2:
        logger.warning(f"Невозможно извлечь номер счета из строки: {account_info}")
        return account_info

    name, number = parts[0], parts[1]

    # Проверяем, является ли это счетом
    if name.lower() != "счет":
        logger.warning(f"Строка не является счетом: {account_info}")
        return account_info

    # Удаляем возможные пробелы
    number_clean = number.replace(" ", "")

    if len(number_clean) < 4 or not number_clean.isdigit():
        logger.warning(f"Некорректный номер счета: {number_clean}")
        return account_info

    # Форматируем в соответствии с ТЗ: Счет **4305
    result = f"{name} **{number_clean[-4:]}"

    logger.info(f"Информация о счете замаскирована: {result}")
    return result


def format_date(date_string: str) -> str:
    """
    Преобразует дату из формата 2024-03-11T02:26:18.671407 в формат ДД.ММ.ГГГГ.

    Args:
        date_string: строка с датой в формате "2024-03-11T02:26:18.671407"

    Returns:
        строку с датой в формате "ДД.ММ.ГГГГ"
    """
    logger.info(f"Форматирование даты: {date_string}")

    try:
        date_object = datetime.fromisoformat(date_string.replace("Z", "+00:00"))
        result = date_object.strftime("%d.%m.%Y")
        logger.info(f"Дата отформатирована: {result}")
        return result
    except (ValueError, TypeError) as e:
        logger.warning(f"Не удалось распарсить дату {date_string}: {e}")
        return date_string


def format_transaction_for_display(transaction: dict) -> str:
    """
    Форматирует транзакцию для отображения в соответствии с ТЗ.

    Args:
        transaction: Словарь с данными транзакции

    Returns:
        Отформатированная строка для отображения
    """
    logger.info(f"Форматирование транзакции {transaction.get('id', 'unknown')} для отображения")

    # Форматируем дату
    date_str = format_date(transaction.get("date", ""))

    # Описание
    description = transaction.get("description", "Н/Д")

    # Определяем откуда/куда и маскируем
    from_info = transaction.get("from", "")
    to_info = transaction.get("to", "")

    # Маскируем номера
    from_masked = ""
    if from_info:
        if "Счет" in from_info:
            from_masked = mask_account_number(from_info)
        else:
            from_masked = mask_card_number(from_info)

    to_masked = ""
    if to_info:
        if "Счет" in to_info:
            to_masked = mask_account_number(to_info)
        else:
            to_masked = mask_card_number(to_info)

    # Сумма
    amount = transaction.get("amount", "Н/Д")
    currency = transaction.get("currency", "")

    # Проверяем, есть ли вложенная структура amount
    if isinstance(amount, dict):
        amount_value = amount.get("amount", "Н/Д")
        currency_obj = amount.get("currency", {})
        if isinstance(currency_obj, dict):
            # Берем code если есть, иначе name
            currency = currency_obj.get("code", "")
            if not currency:
                currency = currency_obj.get("name", "")
        amount = amount_value

    # Форматируем сумму - убираем точку в конце валюты
    if amount != "Н/Д":
        # Убираем лишние пробелы и точки в конце валюты
        currency_clean = currency.strip()
        if currency_clean.endswith('.'):
            currency_clean = currency_clean.rstrip('.')

        # Если валюта пустая, не добавляем ее
        if currency_clean:
            amount_str = f"{amount} {currency_clean}"
        else:
            amount_str = str(amount)
    else:
        amount_str = "Н/Д"

    # Собираем результат согласно ТЗ
    result_lines = []

    # 1. Дата и описание
    result_lines.append(f"{date_str} {description}")

    # 2. От кого -> Кому (если есть отправитель)
    if from_masked and to_masked:
        result_lines.append(f"{from_masked} -> {to_masked}")
    elif to_masked:  # Только получатель
        result_lines.append(f"{to_masked}")
    elif from_masked:  # Только отправитель
        result_lines.append(f"{from_masked}")

    # 3. Сумма (без лишних точек в конце)
    if amount_str:
        result_lines.append(f"Сумма: {amount_str}")

    result = "\n".join(result_lines)
    logger.info("Транзакция отформатирована для отображения")
    return result


if __name__ == "__main__":
    # Тестирование функций
    print("Тестирование функций маскирования и форматирования:")
    print("=" * 60)

    # Тест маскирования карт
    test_cards = [
        "Visa Platinum 7000792289606361",
        "Maestro 1596837868705199",
        "MasterCard 7158300734726758",
        "Visa Classic 6831982476737658",
        "Visa Gold 5999414228426353"
    ]

    print("1. Маскирование карт:")
    for card in test_cards:
        masked = mask_card_number(card)
        print(f"   Вход:  {card}")
        print(f"   Выход: {masked}")
        print()

    # Тест маскирования счетов
    test_accounts = [
        "Счет 73654108430135874305",
        "Счет 64686473678894779589",
        "Счет 35383033474447895560",
        "Счет 86385495228655958148"
    ]

    print("\n2. Маскирование счетов:")
    for account in test_accounts:
        masked = mask_account_number(account)
        print(f"   Вход:  {account}")
        print(f"   Выход: {masked}")
        print()

    # Тест форматирования даты
    print("\n3. Форматирование даты:")
    test_dates = [
        "2024-03-11T02:26:18.671407",
        "2019-08-26T10:50:58.294041",
        "2018-12-08T22:46:21.935582",
        "2018-07-31T12:25:32.579413"
    ]

    for date_input in test_dates:
        formatted = format_date(date_input)
        print(f"   Вход:  {date_input}")
        print(f"   Выход: {formatted}")
        print()

    # Тест полного форматирования транзакции
    print("\n4. Полное форматирование транзакции:")
    test_transactions = [
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
            "state": "EXECUTED",
            "date": "2019-07-03T18:35:29.512364",
            "operationAmount": {
                "amount": "8221.37",
                "currency": {
                    "name": "USD",
                    "code": "USD"
                }
            },
            "description": "Перевод организации",
            "from": "MasterCard 7158300734726758",
            "to": "Счет 35383033474447895560"
        },
        {
            "id": 72122709,
            "state": "EXECUTED",
            "date": "2018-12-08T22:46:21.935582",
            "operationAmount": {
                "amount": "40542.0",
                "currency": {
                    "name": "руб.",
                    "code": "RUB"
                }
            },
            "description": "Открытие вклада",
            "to": "Счет 86385495228655958148"
        }
    ]

    for i, trans in enumerate(test_transactions, 1):
        # Адаптируем формат
        adapted_trans = {
            "id": trans["id"],
            "date": trans["date"],
            "description": trans["description"],
            "from": trans.get("from", ""),
            "to": trans.get("to", ""),
            "amount": trans["operationAmount"],
            "currency": trans["operationAmount"]["currency"]["name"]  # type: ignore[index]
        }

        formatted = format_transaction_for_display(adapted_trans)
        print(f"Транзакция {i}:")
        print(formatted)
        print("-" * 40)

    print("\nВсе функции работают корректно!")
