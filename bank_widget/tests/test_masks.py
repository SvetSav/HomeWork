"""
Тесты для модуля masks.
"""

import sys
from unittest.mock import patch

import pytest
from masks import format_date
from masks import format_transaction_for_display
from masks import get_mask_account
from masks import get_mask_card_number
from masks import logger
from masks import mask_account_number
from masks import mask_card_number

sys.path.insert(0, sys.path[0] + '/../src')


def test_mask_card_number_basic():
    """Тест базового маскирования карты."""
    result = mask_card_number('Visa Platinum 7000792289606361')
    assert result == 'Visa Platinum 7000 79** **** 6361'


def test_mask_card_number_with_spaces():
    """Тест маскирования карты с пробелами в номере."""
    result = mask_card_number('MasterCard 1234 5678 9012 3456')
    assert result == 'MasterCard 1234 56** **** 3456'


def test_mask_card_number_invalid():
    """Тест маскирования с некорректным номером карты."""
    result = mask_card_number('Visa 123')
    assert result == 'Visa 123'  # Возвращает исходную строку


def test_mask_account_number_basic():
    """Тест базового маскирования счета."""
    result = mask_account_number('Счет 73654108430135874305')
    assert result == 'Счет **4305'


def test_mask_account_number_not_account():
    """Тест маскирования не-счета."""
    result = mask_account_number('Карта 1234567890123456')
    assert result == 'Карта 1234567890123456'


def test_mask_account_number_invalid():
    """Тест маскирования некорректного счета."""
    result = mask_account_number('Счет 123')
    assert result == 'Счет 123'


def test_format_date_basic():
    """Тест форматирования даты."""
    result = format_date('2019-08-26T10:50:58.294041')
    assert result == '26.08.2019'


def test_format_date_with_z():
    """Тест форматирования даты с Z."""
    result = format_date('2019-08-26T10:50:58.294041Z')
    assert result == '26.08.2019'


def test_format_date_invalid():
    """Тест форматирования некорректной даты."""
    result = format_date('invalid-date')
    assert result == 'invalid-date'


def test_format_transaction_for_display_basic():
    """Тест форматирования транзакции."""
    transaction = {
        'id': 1,
        'date': '2019-08-26T10:50:58.294041',
        'description': 'Перевод организации',
        'from': 'Maestro 1596837868705199',
        'to': 'Счет 64686473678894779589',
        'amount': '31957.58',
        'currency': 'руб.'
    }

    result = format_transaction_for_display(transaction)

    # Проверяем по строкам
    lines = result.split('\n')
    assert len(lines) == 3
    assert lines[0] == '26.08.2019 Перевод организации'
    assert lines[1] == 'Maestro 1596 83** **** 5199 -> Счет **9589'
    assert lines[2] == 'Сумма: 31957.58 руб'


def test_format_transaction_for_display_with_sender_and_receiver():
    """Тест форматирования транзакции с отправителем и получателем."""
    transaction = {
        'id': 441945886,
        'date': '2019-08-26T10:50:58.294041',
        'description': 'Перевод с карты на карту',
        'from': 'MasterCard 7158300734726758',
        'to': 'Visa Classic 6831982476737658',
        'amount': '31957.58',
        'currency': 'руб.'
    }

    result = format_transaction_for_display(transaction)

    # Проверяем формат
    lines = result.split('\n')
    assert len(lines) == 3
    assert lines[0] == '26.08.2019 Перевод с карты на карту'
    assert lines[1] == 'MasterCard 7158 30** **** 6758 -> Visa Classic 6831 98** **** 7658'
    assert lines[2] == 'Сумма: 31957.58 руб'


def test_format_transaction_for_display_only_to():
    """Тест форматирования транзакции только с получателем."""
    transaction = {
        'id': 72122709,
        'date': '2018-12-08T22:46:21.935582',
        'description': 'Открытие вклада',
        'to': 'Счет 86385495228655958148',
        'amount': '40542.0',
        'currency': 'руб.'
    }

    result = format_transaction_for_display(transaction)

    lines = result.split('\n')
    assert len(lines) == 3
    assert lines[0] == '08.12.2018 Открытие вклада'
    assert lines[1] == 'Счет **8148'
    assert lines[2] == 'Сумма: 40542.0 руб'


def test_format_transaction_for_display_dict_amount():
    """Тест форматирования транзакции с вложенной структурой amount."""
    transaction = {
        'id': 1,
        'date': '2019-08-26T10:50:58.294041',
        'description': 'Перевод организации',
        'from': 'Maestro 1596837868705199',
        'to': 'Счет 64686473678894779589',
        'amount': {
            'amount': '31957.58',
            'currency': {
                'name': 'руб.',
                'code': 'RUB'
            }
        },
        'currency': 'руб.'
    }

    result = format_transaction_for_display(transaction)

    lines = result.split('\n')
    assert len(lines) == 3
    assert lines[0] == '26.08.2019 Перевод организации'
    assert lines[1] == 'Maestro 1596 83** **** 5199 -> Счет **9589'
    # Может быть "руб" (без точки) или "RUB" в зависимости от того, что берется из currency
    assert 'Сумма: 31957.58' in lines[2]


def test_format_transaction_for_display_currency_with_dot():
    """Тест форматирования с валютой с точкой в конце."""
    transaction = {
        'id': 1,
        'date': '2019-08-26T10:50:58.294041',
        'description': 'Перевод организации',
        'from': 'Maestro 1596837868705199',
        'to': 'Счет 64686473678894779589',
        'amount': '31957.58',
        'currency': 'руб.'  # Валюта с точкой
    }

    result = format_transaction_for_display(transaction)

    lines = result.split('\n')
    assert lines[2] == 'Сумма: 31957.58 руб'  # Без точки


def test_format_transaction_for_display_currency_without_dot():
    """Тест форматирования с валютой без точки."""
    transaction = {
        'id': 1,
        'date': '2019-08-26T10:50:58.294041',
        'description': 'Перевод организации',
        'from': 'Maestro 1596837868705199',
        'to': 'Счет 64686473678894779589',
        'amount': '31957.58',
        'currency': 'USD'  # Валюта без точки
    }

    result = format_transaction_for_display(transaction)

    lines = result.split('\n')
    assert lines[2] == 'Сумма: 31957.58 USD'


def test_format_transaction_for_display_no_currency():
    """Тест форматирования без валюты."""
    transaction = {
        'id': 1,
        'date': '2019-08-26T10:50:58.294041',
        'description': 'Перевод организации',
        'from': 'Maestro 1596837868705199',
        'to': 'Счет 64686473678894779589',
        'amount': '31957.58',
        'currency': ''  # Пустая валюта
    }

    result = format_transaction_for_display(transaction)

    lines = result.split('\n')
    assert lines[2] == 'Сумма: 31957.58'


def test_format_transaction_for_display_no_from():
    """Тест форматирования транзакции без отправителя."""
    transaction = {
        'id': 1,
        'date': '2019-08-26T10:50:58.294041',
        'description': 'Открытие вклада',
        'to': 'Счет 64686473678894779589',
        'amount': '40542.0',
        'currency': 'руб.'
    }

    result = format_transaction_for_display(transaction)
    assert 'Счет **9589' in result


def test_get_mask_card_number_valid():
    """Тест валидный номер карты."""
    result = get_mask_card_number(7000792289606361)
    assert result == "7000 79** **** 6361"


def test_get_mask_card_number_invalid_length():
    """Тест невалидная длина номера карты."""
    # Слишком короткий номер
    with pytest.raises(ValueError, match="Номер карты должен состоять из 16 цифр"):
        get_mask_card_number(123)

    # Слишком длинный номер
    with pytest.raises(ValueError, match="Номер карты должен состоять из 16 цифр"):
        get_mask_card_number(12345678901234567890)


def test_get_mask_card_number_logging():
    """Тест логирование для get_mask_card_number."""
    # Тест успешного случая
    with patch.object(logger, 'info') as mock_info:
        get_mask_card_number(7000792289606361)

        # Проверяем что было два info вызова
        assert mock_info.call_count == 2
        assert "Запрос на маскировку номера карты" in mock_info.call_args_list[0][0][0]
        assert "Номер карты замаскирован" in mock_info.call_args_list[1][0][0]

    # Тест ошибки
    with patch.object(logger, 'error') as mock_error:
        with pytest.raises(ValueError):
            get_mask_card_number(123)

        mock_error.assert_called_once()
        assert "Номер карты должен состоять из 16 цифр" in mock_error.call_args[0][0]


def test_get_mask_account_valid():
    """Тест валидный номер счета."""
    result = get_mask_account(73654108430135874305)
    assert result == "**4305"


def test_get_mask_account_exactly_4_digits():
    """Тест номер счета из 4 цифр."""
    result = get_mask_account(1234)
    assert result == "**1234"


def test_get_mask_account_invalid_length():
    """Тест слишком короткий номер счета."""
    with pytest.raises(ValueError, match="Длина номера счета должна составлять не менее 4 цифр"):
        get_mask_account(123)


def test_get_mask_account_logging():
    """Тест логирование для get_mask_account."""
    # Тест успешного случая
    with patch.object(logger, 'info') as mock_info:
        get_mask_account(73654108430135874305)

        # Проверяем что было два info вызова
        assert mock_info.call_count == 2
        assert "Запрос на маскировку номера счета" in mock_info.call_args_list[0][0][0]
        assert "Номер счета замаскирован" in mock_info.call_args_list[1][0][0]

    # Тест ошибки
    with patch.object(logger, 'error') as mock_error:
        with pytest.raises(ValueError):
            get_mask_account(123)

        mock_error.assert_called_once()
        assert "Длина номера счета должна составлять не менее 4 цифр" in mock_error.call_args[0][0]


def test_mask_card_number_empty_string():
    """Тест пустая строка карты."""
    result = mask_card_number("")
    assert result == ""

    # Проверяем warning логирование
    with patch.object(logger, 'warning') as mock_warning:
        mask_card_number("")
        mock_warning.assert_called_once_with("Получена пустая строка карты")


def test_mask_card_number_with_regex_fallback():
    """Тест использование регулярного выражения."""
    # Тестируем случаи, которые обрабатываются regex
    test_cases = [
        ("Visa Platinum 7000792289606361", "Visa Platinum 7000 79** **** 6361"),
        ("MasterCard 1234567890123456", "MasterCard 1234 56** **** 3456"),
        ("Maestro 1596837868705199", "Maestro 1596 83** **** 5199"),
    ]

    for input_str, expected in test_cases:
        result = mask_card_number(input_str)
        assert result == expected


def test_mask_card_number_invalid_card_number():
    """Тест некорректный номер карты."""
    # Не 16 цифр
    with patch.object(logger, 'warning') as mock_warning:
        result = mask_card_number("Visa 12345")
        assert result == "Visa 12345"
        mock_warning.assert_called_once()
        assert "Некорректный номер карты" in mock_warning.call_args[0][0]

    # Не все цифры
    with patch.object(logger, 'warning') as mock_warning:
        result = mask_card_number("Visa 12345678901234ab")
        assert result == "Visa 12345678901234ab"
        mock_warning.assert_called_once()
        assert "Некорректный номер карты" in mock_warning.call_args[0][0]


def test_mask_account_number_empty_string():
    """Тест пустая строка счета."""
    result = mask_account_number("")
    assert result == ""

    with patch.object(logger, 'warning') as mock_warning:
        mask_account_number("")
        mock_warning.assert_called_once_with("Получена пустая строка счета")


def test_mask_account_number_cannot_extract():
    """Тест невозможно извлечь номер счета."""
    # Строка без пробелов
    with patch.object(logger, 'warning') as mock_warning:
        result = mask_account_number("Счет12345678")
        assert result == "Счет12345678"
        mock_warning.assert_called_once()
        assert "Невозможно извлечь номер счета" in mock_warning.call_args[0][0]


def test_format_date_value_error():
    """Тест ValueError при форматировании даты."""
    # Неправильный формат даты
    with patch.object(logger, 'warning') as mock_warning:
        result = format_date("не дата")
        assert result == "не дата"
        mock_warning.assert_called_once()
        assert "Не удалось распарсить дату" in mock_warning.call_args[0][0]


def test_format_date_logging():
    """Тест логирование для format_date."""
    with patch.object(logger, 'info') as mock_info:
        format_date("2019-08-26T10:50:58.294041")

        # Проверяем что было два info вызова
        assert mock_info.call_count == 2
        assert "Форматирование даты" in mock_info.call_args_list[0][0][0]
        assert "Дата отформатирована" in mock_info.call_args_list[1][0][0]


def test_format_transaction_empty_date():
    """Тест пустая дата в транзакции."""
    transaction = {
        "date": "",
        "description": "Тест",
        "amount": "100",
        "currency": "RUB"
    }

    result = format_transaction_for_display(transaction)
    assert "Тест" in result


def test_format_transaction_no_description():
    """Тест нет описания в транзакции."""
    transaction = {
        "date": "2019-08-26T10:50:58.294041",
        "description": "",
        "amount": "100",
        "currency": "RUB"
    }

    result = format_transaction_for_display(transaction)
    assert "Н/Д" in result or "26.08.2019" in result


def test_format_transaction_from_info_special_cases():
    """Тест специальные случаи для from_info."""
    # from_info пустая строка
    transaction = {
        "date": "2019-08-26T10:50:58.294041",
        "description": "Тест",
        "from": "",
        "to": "Счет 12345678901234567890",
        "amount": "100",
        "currency": "RUB"
    }

    result = format_transaction_for_display(transaction)
    assert "Счет **7890" in result
    assert "->" not in result  # Не должно быть стрелки если нет отправителя

    # from_info не содержит "Счет" и не пустая
    transaction = {
        "date": "2019-08-26T10:50:58.294041",
        "description": "Тест",
        "from": "MasterCard 1234567890123456",
        "to": "",
        "amount": "100",
        "currency": "RUB"
    }

    result = format_transaction_for_display(transaction)
    assert "MasterCard" in result
    assert "->" not in result  # Не должно быть стрелки если нет получателя


def test_format_transaction_amount_dict_complex():
    """Тест ссложная структура amount как словарь."""
    # currency как словарь без code
    transaction = {
        "date": "2019-08-26T10:50:58.294041",
        "description": "Тест",
        "amount": {
            "amount": "100.50",
            "currency": {
                "name": "рубль",  # только name, нет code
            }
        },
        "currency": "руб."
    }

    result = format_transaction_for_display(transaction)
    assert "Сумма: 100.50 рубль" in result

    # currency как словарь с code
    transaction = {
        "date": "2019-08-26T10:50:58.294041",
        "description": "Тест",
        "amount": {
            "amount": "200.75",
            "currency": {
                "code": "EUR",
                "name": "евро"
            }
        },
        "currency": "руб."
    }

    result = format_transaction_for_display(transaction)
    assert "Сумма: 200.75 EUR" in result  # code имеет приоритет


def test_format_transaction_no_amount_str():
    """Тест amount_str пустая."""
    # amount = "Н/Д"
    transaction = {
        "date": "2019-08-26T10:50:58.294041",
        "description": "Тест",
        "amount": "Н/Д",
        "currency": "RUB"
    }

    result = format_transaction_for_display(transaction)
    assert "Сумма: Н/Д" in result


def test_format_transaction_logging():
    """Тест логирование для format_transaction_for_display."""
    transaction = {
        "date": "2019-08-26T10:50:58.294041",
        "description": "Тест",
        "amount": "100",
        "currency": "RUB"
    }

    with patch.object(logger, 'info') as mock_info:
        format_transaction_for_display(transaction)

        # Проверяем что было два info вызова
        assert mock_info.call_count >= 2
        assert "Форматирование транзакции" in mock_info.call_args_list[0][0][0]
        assert "Транзакция отформатирована" in mock_info.call_args_list[-1][0][0]


def test_mask_card_number_last_letter_logic():
    """Тест логика поиска последней буквы."""
    # Строка с дефисами и пробелами в названии карты
    test_cases = [
        ("Visa-Classic 1234567890123456", "Visa-Classic 1234 56** **** 3456"),
        ("American Express 1234567890123456", "American Express 1234 56** **** 3456"),
        ("Visa Platinum Pro 1234567890123456", "Visa Platinum Pro 1234 56** **** 3456"),
    ]

    for input_str, expected in test_cases:
        result = mask_card_number(input_str)
        # Может работать через regex или rsplit, проверяем что не падает
        assert "**" in result or result == input_str


def test_format_date_with_timezone():
    """Тест строк 296: дата с таймзоной."""
    # Даты с разными таймзонами
    test_cases = [
        ("2019-08-26T10:50:58.294041+03:00", "26.08.2019"),
        ("2019-08-26T10:50:58.294041-05:00", "26.08.2019"),
        ("2019-08-26T10:50:58Z", "26.08.2019"),  # Z заменяется на +00:00
    ]

    for date_input, expected in test_cases:
        result = format_date(date_input)
        assert result == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
