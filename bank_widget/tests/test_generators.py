"""
Тесты для модуля generators.
"""

from typing import Any
from typing import Dict
from typing import List

import pytest
from src.generators import card_number_generator  # noqa: E402
from src.generators import filter_by_currency  # noqa: E402
from src.generators import transaction_descriptions  # noqa: E402


# Фикстуры для тестовых данных
@pytest.fixture
def sample_transactions() -> List[Dict[str, Any]]:
    """Фикстура с тестовыми транзакциями."""
    return [
        {
            "id": 939719570,
            "state": "EXECUTED",
            "date": "2018-06-30T02:08:58.425572",
            "operationAmount": {
                "amount": "9824.07",
                "currency": {"name": "USD", "code": "USD"}
            },
            "description": "Перевод организации",
            "from": "Счет 75106830613657916952",
            "to": "Счет 11776614605963066702"
        },
        {
            "id": 142264268,
            "state": "EXECUTED",
            "date": "2019-04-04T23:20:05.206878",
            "operationAmount": {
                "amount": "79114.93",
                "currency": {"name": "USD", "code": "USD"}
            },
            "description": "Перевод со счета на счет",
            "from": "Счет 19708645243227258542",
            "to": "Счет 75651667383060284188"
        },
        {
            "id": 873106923,
            "state": "EXECUTED",
            "date": "2019-03-23T01:09:46.296404",
            "operationAmount": {
                "amount": "43318.34",
                "currency": {"name": "руб.", "code": "RUB"}
            },
            "description": "Перевод со счета на счет",
            "from": "Счет 44812258784861134719",
            "to": "Счет 74489636417521191160"
        },
        {
            "id": 895315941,
            "state": "EXECUTED",
            "date": "2018-08-19T04:27:37.904916",
            "operationAmount": {
                "amount": "56883.54",
                "currency": {"name": "USD", "code": "USD"}
            },
            "description": "Перевод с карты на карту",
            "from": "Visa Classic 6831982476737658",
            "to": "Visa Platinum 8990922113665229"
        }
    ]


@pytest.fixture
def transactions_without_currency() -> List[Dict[str, Any]]:
    """Фикстура с транзакциями без поля currency."""
    return [
        {"id": 1, "description": "Транзакция 1"},
        {"id": 2, "operationAmount": {"amount": "100"}},
        {"id": 3, "operationAmount": {"currency": {}}}
    ]


# Тесты для filter_by_currency
class TestFilterByCurrency:
    """Тесты для функции filter_by_currency."""

    def test_filter_usd_transactions(self, sample_transactions: List[Dict[str, Any]]) -> None:
        """Тест фильтрации USD транзакций."""
        usd_gen = filter_by_currency(sample_transactions, "USD")
        usd_transactions = list(usd_gen)

        assert len(usd_transactions) == 3
        assert all(
            t["operationAmount"]["currency"]["code"] == "USD"
            for t in usd_transactions
        )
        assert usd_transactions[0]["id"] == 939719570
        assert usd_transactions[1]["id"] == 142264268
        assert usd_transactions[2]["id"] == 895315941

    def test_filter_rub_transactions(self, sample_transactions: List[Dict[str, Any]]) -> None:
        """Тест фильтрации RUB транзакций."""
        rub_gen = filter_by_currency(sample_transactions, "RUB")
        rub_transactions = list(rub_gen)

        assert len(rub_transactions) == 1
        assert rub_transactions[0]["id"] == 873106923
        assert rub_transactions[0]["operationAmount"]["currency"]["code"] == "RUB"

    def test_filter_nonexistent_currency(self, sample_transactions: List[Dict[str, Any]]) -> None:
        """Тест фильтрации несуществующей валюты."""
        eur_gen = filter_by_currency(sample_transactions, "EUR")
        eur_transactions = list(eur_gen)

        assert len(eur_transactions) == 0

    def test_empty_transactions_list(self) -> None:
        """Тест с пустым списком транзакций."""
        empty_gen = filter_by_currency([], "USD")
        assert list(empty_gen) == []

    def test_transactions_missing_currency_field(self, transactions_without_currency: List[Dict[str, Any]]) -> None:
        """Тест с транзакциями без поля currency."""
        gen = filter_by_currency(transactions_without_currency, "USD")
        assert list(gen) == []

    def test_generator_behavior(self, sample_transactions: List[Dict[str, Any]]) -> None:
        """Тест поведения генератора (по одному элементу)."""
        usd_gen = filter_by_currency(sample_transactions, "USD")

        # Получаем первый элемент
        first = next(usd_gen)
        assert first["id"] == 939719570

        # Получаем второй элемент
        second = next(usd_gen)
        assert second["id"] == 142264268

        # Получаем все оставшиеся
        remaining = list(usd_gen)
        assert len(remaining) == 1
        assert remaining[0]["id"] == 895315941

    @pytest.mark.parametrize("currency,expected_count", [
        ("USD", 3),
        ("RUB", 1),
        ("EUR", 0),
    ])
    def test_filter_parametrized(self, sample_transactions: List[Dict[str, Any]],
                                 currency: str, expected_count: int) -> None:
        """Параметризованный тест фильтрации по разным валютам."""
        gen = filter_by_currency(sample_transactions, currency)
        transactions = list(gen)
        assert len(transactions) == expected_count


# Тесты для transaction_descriptions
class TestTransactionDescriptions:
    """Тесты для функции transaction_descriptions."""

    def test_get_all_descriptions(self, sample_transactions: List[Dict[str, Any]]) -> None:
        """Тест получения всех описаний."""
        desc_gen = transaction_descriptions(sample_transactions)
        descriptions = list(desc_gen)

        assert len(descriptions) == 4
        assert descriptions == [
            "Перевод организации",
            "Перевод со счета на счет",
            "Перевод со счета на счет",
            "Перевод с карты на карту"
        ]

    def test_empty_transactions(self) -> None:
        """Тест с пустым списком транзакций."""
        desc_gen = transaction_descriptions([])
        assert list(desc_gen) == []

    def test_transactions_without_description(self) -> None:
        """Тест с транзакциями без описания."""
        transactions: List[Dict[str, Any]] = [
            {"id": 1, "description": "Описание 1"},
            {"id": 2, "description": None},  # Явно указываем None
            {"id": 3, "description": "Описание 3"}
        ]
        desc_gen = transaction_descriptions(transactions)
        descriptions = list(desc_gen)

        assert descriptions == ["Описание 1", "Описание 3"]

    def test_generator_behavior_one_by_one(self, sample_transactions: List[Dict[str, Any]]) -> None:
        """Тест получения описаний по одному."""
        desc_gen = transaction_descriptions(sample_transactions)

        assert next(desc_gen) == "Перевод организации"
        assert next(desc_gen) == "Перевод со счета на счет"
        assert next(desc_gen) == "Перевод со счета на счет"
        assert next(desc_gen) == "Перевод с карты на карту"

        with pytest.raises(StopIteration):
            next(desc_gen)


# Тесты для card_number_generator
class TestCardNumberGenerator:
    """Тесты для функции card_number_generator."""

    @pytest.mark.parametrize("start,end,expected", [
        (1, 3, ["0000 0000 0000 0001", "0000 0000 0000 0002", "0000 0000 0000 0003"]),
        (9999999999999997, 9999999999999999, [
            "9999 9999 9999 9997",
            "9999 9999 9999 9998",
            "9999 9999 9999 9999"
        ]),
        (1234567890123456, 1234567890123456, ["1234 5678 9012 3456"]),
    ])
    def test_generate_card_numbers(self, start: int, end: int, expected: List[str]) -> None:
        """Параметризованный тест генерации номеров карт."""
        gen = card_number_generator(start, end)
        result = list(gen)
        assert result == expected

    def test_single_card_number(self) -> None:
        """Тест генерации одного номера карты."""
        gen = card_number_generator(42, 42)
        result = list(gen)
        assert result == ["0000 0000 0000 0042"]

    def test_large_range(self) -> None:
        """Тест генерации большого диапазона."""
        gen = card_number_generator(1, 5)
        result = list(gen)
        assert len(result) == 5
        assert result[0] == "0000 0000 0000 0001"
        assert result[4] == "0000 0000 0000 0005"

    def test_format_correctness(self) -> None:
        """Тест правильности форматирования."""
        gen = card_number_generator(1234567890123456, 1234567890123456)
        result = next(gen)
        # Проверяем формат: 4 группы по 4 цифры, разделенные пробелами
        assert len(result) == 19  # 16 цифр + 3 пробела
        assert result.count(" ") == 3
        groups = result.split(" ")
        assert len(groups) == 4
        assert all(len(g) == 4 for g in groups)

    def test_invalid_start_value(self) -> None:
        """Тест с некорректным начальным значением."""
        with pytest.raises(ValueError, match="Начальное значение должно быть не менее 1"):
            list(card_number_generator(0, 5))

    def test_invalid_end_value(self) -> None:
        """Тест с некорректным конечным значением."""
        with pytest.raises(ValueError, match="Конечное значение не должно превышать 9999999999999999"):
            list(card_number_generator(1, 10000000000000000))

    def test_start_greater_than_end(self) -> None:
        """Тест когда start > end."""
        with pytest.raises(ValueError, match="Начальное значение должно быть меньше или равно конечному"):
            list(card_number_generator(10, 5))

    def test_generator_behavior(self) -> None:
        """Тест поведения генератора (по одному элементу)."""
        gen = card_number_generator(1, 3)

        assert next(gen) == "0000 0000 0000 0001"
        assert next(gen) == "0000 0000 0000 0002"
        assert next(gen) == "0000 0000 0000 0003"

        with pytest.raises(StopIteration):
            next(gen)


def test_filter_by_currency_case_insensitive():
    transactions = [
        {"id": 1, "currency": "USD"},
        {"id": 2, "currency": "usd"},  # нижний регистр
        {"id": 3, "currency": "UsD"},  # смешанный регистр
        {"id": 4, "currency": "RUB"},
        {"id": 5, "operationAmount": {"currency": {"code": "EUR"}}},
        {"id": 6, "operationAmount": {"currency": {"code": "eur"}}},  # нижний регистр
    ]

    # Поиск в нижнем регистре
    gen = filter_by_currency(transactions, "usd")
    result = list(gen)
    assert len(result) == 3
    assert {t["id"] for t in result} == {1, 2, 3}

    # Поиск в верхнем регистре
    gen = filter_by_currency(transactions, "USD")
    result = list(gen)
    assert len(result) == 3

    # Поиск в смешанном регистре
    gen = filter_by_currency(transactions, "Usd")
    result = list(gen)
    assert len(result) == 3

    # Проверка EUR
    gen = filter_by_currency(transactions, "eur")
    result = list(gen)
    assert len(result) == 2
    assert {t["id"] for t in result} == {5, 6}


def test_filter_by_currency_json_format_with_continue():
    transactions = [
        {
            "id": 1,
            "operationAmount": {
                "amount": "100",
                "currency": {"name": "USD", "code": "USD"}
            },
            "currency": "EUR"  # Дополнительное поле currency, не должно мешать
        },
        {
            "id": 2,
            "operationAmount": {
                "amount": "200",
                "currency": {"name": "RUB", "code": "RUB"}
            }
        }
    ]

    # Должен найти только первую транзакцию по USD
    gen = filter_by_currency(transactions, "USD")
    result = list(gen)
    assert len(result) == 1
    assert result[0]["id"] == 1

    # Проверяем что continue работает - вторая транзакция не проверяет поле currency
    gen = filter_by_currency(transactions, "RUB")
    result = list(gen)
    assert len(result) == 1
    assert result[0]["id"] == 2


def test_filter_by_currency_nested_dict_format():
    # Use proper typing with explicit dictionary structure
    transactions: List[Dict[str, Any]] = [
        {"id": 1, "currency": {"code": "USD", "name": "Доллар"}},
        {"id": 2, "currency": {"code": "RUB", "name": "Рубль"}},
        {"id": 3, "currency": {"code": "EUR"}},  # Без name
        {"id": 4, "currency": {"name": "Йена"}},  # Без code
        {"id": 5, "currency": {}},  # Пустой словарь
        {"id": 6, "currency": "USD"},  # Простая строка
        {"id": 7, "currency": None},  # None значение
        {"id": 8, "currency": 123},  # Не строка и не словарь
    ]

    # Тестируем поиск USD
    gen = filter_by_currency(transactions, 'USD')
    result = list(gen)
    assert len(result) == 2  # id:1 и id:6
    assert {t["id"] for t in result} == {1, 6}

    # Тестируем поиск RUB
    gen = filter_by_currency(transactions, "RUB")
    result = list(gen)
    assert len(result) == 1
    assert result[0]["id"] == 2

    # Тестируем поиск EUR
    gen = filter_by_currency(transactions, "EUR")
    result = list(gen)
    assert len(result) == 1
    assert result[0]["id"] == 3


def test_filter_by_currency_mixed_formats():
    transactions = [
        # Формат JSON
        {
            "id": 1,
            "operationAmount": {
                "amount": "100.50",
                "currency": {"code": "USD", "name": "US Dollar"}
            }
        },
        # Формат CSV
        {"id": 2, "currency": "USD", "amount": 200.75},
        # Формат с вложенностью
        {"id": 3, "currency": {"code": "USD", "name": "Доллар"}},
        # Формат с ошибками
        {"id": 4, "operationAmount": "invalid"},  # operationAmount не словарь
        {"id": 5, "operationAmount": {"currency": "invalid"}},  # currency не словарь
        {"id": 6, "operationAmount": {"currency": {"code": None}}},  # code = None
        {"id": 7, "operationAmount": {"currency": {"code": ""}}},  # пустая строка
    ]

    gen = filter_by_currency(transactions, "USD")
    result = list(gen)
    assert len(result) == 3
    assert {t["id"] for t in result} == {1, 2, 3}


def test_filter_by_currency_attribute_errors():
    transactions: List[Dict[str, Any]] = [
        {"id": 1, "operationAmount": "not a dict"},  # вызовет AttributeError при .get()
        {"id": 2, "operationAmount": {"currency": "not a dict"}},  # вызовет AttributeError
        {"id": 3},  # нет operationAmount вообще
        {"id": 4, "operationAmount": {"amount": "100"}},  # нет currency
        {"id": 5, "operationAmount": {"currency": {}}},  # пустой словарь currency
    ]

    # Не должно падать с исключениями
    gen = filter_by_currency(transactions, "USD")
    result = list(gen)
    assert result == []  # Ничего не найдено


def test_card_number_generator_edge_cases():
    # Проверка минимального значения
    gen = card_number_generator(1, 1)
    result = list(gen)
    assert result == ["0000 0000 0000 0001"]

    # Проверка максимального значения
    gen = card_number_generator(9999999999999999, 9999999999999999)
    result = list(gen)
    assert result == ["9999 9999 9999 9999"]

    # Проверка форматирования с ведущими нулями
    gen = card_number_generator(123, 123)
    result = list(gen)
    assert result == ["0000 0000 0000 0123"]

    # Проверка чисел с разным количеством цифр
    gen = card_number_generator(7, 10)
    result = list(gen)
    assert result == [
        "0000 0000 0000 0007",
        "0000 0000 0000 0008",
        "0000 0000 0000 0009",
        "0000 0000 0000 0010"
    ]


def test_card_number_generator_special_cases():
    # Число с 15 цифрами (должно добавить один ведущий ноль)
    gen = card_number_generator(123456789012345, 123456789012345)
    result = list(gen)
    assert result == ["0123 4567 8901 2345"]

    # Число с 1 цифрой
    gen = card_number_generator(9, 9)
    result = list(gen)
    assert result == ["0000 0000 0000 0009"]

    # Число с 16 цифрами без ведущих нулей
    gen = card_number_generator(1234567890123456, 1234567890123456)
    result = list(gen)
    assert result == ["1234 5678 9012 3456"]

    # Проверка правильности разделения на группы
    gen = card_number_generator(1234567812345678, 1234567812345678)
    result = list(gen)
    assert result == ["1234 5678 1234 5678"]

    # Проверка граничных значений
    gen = card_number_generator(9999999999999990, 9999999999999993)
    result = list(gen)
    assert result == [
        "9999 9999 9999 9990",
        "9999 9999 9999 9991",
        "9999 9999 9999 9992",
        "9999 9999 9999 9993"
    ]


def test_card_number_generator_negative_tests():
    # Проверка минимального допустимого значения (1)
    with pytest.raises(ValueError, match="Начальное значение должно быть не менее 1"):
        list(card_number_generator(0, 5))

    # Проверка отрицательного значения
    with pytest.raises(ValueError, match="Начальное значение должно быть не менее 1"):
        list(card_number_generator(-1, 5))

    # Проверка превышения максимума
    with pytest.raises(ValueError, match="Конечное значение не должно превышать 9999999999999999"):
        list(card_number_generator(1, 10000000000000000))

    # Проверка start > end
    with pytest.raises(ValueError, match="Начальное значение должно быть меньше или равно конечному"):
        list(card_number_generator(10, 1))

    # Проверка равных значений (должно работать)
    gen = card_number_generator(5, 5)
    result = list(gen)
    assert result == ["0000 0000 0000 0005"]


def test_generator_stop_iteration():
    # Для filter_by_currency
    transactions = [{"id": 1, "currency": "USD"}]
    gen1 = filter_by_currency(transactions, "USD")
    assert next(gen1)["id"] == 1
    with pytest.raises(StopIteration):
        next(gen1)

    # Для transaction_descriptions
    gen2 = transaction_descriptions([{"description": "test"}])
    assert next(gen2) == "test"
    with pytest.raises(StopIteration):
        next(gen2)

    # Для card_number_generator
    gen3 = card_number_generator(1, 1)
    assert next(gen3) == "0000 0000 0000 0001"
    with pytest.raises(StopIteration):
        next(gen3)


def test_transaction_descriptions_various_types():
    transactions: List[Dict[str, Any]] = [
        {"id": 1, "description": "Строка"},  # truthy
        {"id": 2, "description": 123},  # truthy (не 0)
        {"id": 3, "description": 12.34},  # truthy (не 0.0)
        {"id": 4, "description": True},  # truthy
        {"id": 5, "description": ["список"]},  # truthy (не пустой список)
        {"id": 6, "description": {"dict": "value"}},  # truthy (не пустой словарь)
        {"id": 7, "description": False},  # falsy - пропустится
        {"id": 8, "description": 0},  # falsy - пропустится
        {"id": 9, "description": []},  # falsy - пропустится
        {"id": 10, "description": {}},  # falsy - пропустится
        {"id": 11, "description": ""},  # falsy - пропустится
        {"id": 12, "description": None},  # falsy - пропустится
        {"id": 13, "description": 0.0},  # falsy - пропустится
    ]

    gen = transaction_descriptions(transactions)
    result = list(gen)

    # The assertion at line 541 was marked unreachable because the previous
    # line might fail if transaction_descriptions has type issues
    # Make sure to import transaction_descriptions properly
    assert len(result) == 6
    assert result[0] == "Строка"
    assert result[1] == 123
    assert result[2] == 12.34
    assert result[3] is True
    assert result[4] == ["список"]  # type: ignore[unreachable]
    assert result[5] == {"dict": "value"}
