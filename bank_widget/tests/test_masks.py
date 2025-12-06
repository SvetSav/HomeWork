"""
Тесты для модуля masks.
"""

import os
import sys

# Добавляем src в путь для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


import pytest  # noqa: E402
from masks import get_mask_account  # type: ignore[import-not-found]  # noqa: E402
from masks import get_mask_card_number  # noqa: E402


class TestMasks:
    """Тесты для функций маскировки."""

    @pytest.mark.parametrize("card_number, expected", [
        (7000792289606361, "7000 79** **** 6361"),
        (1596837868705199, "1596 83** **** 5199"),
        (7158300734726758, "7158 30** **** 6758"),
        (6831982476737658, "6831 98** **** 7658"),
    ])
    def test_get_mask_card_number_valid(self, card_number: int, expected: str) -> None:
        """Тест маскировки валидного номера карты."""
        result = get_mask_card_number(card_number)
        assert result == expected

    @pytest.mark.parametrize("invalid_card", [
        123,  # слишком короткий
        12345678901234567890,  # слишком длинный
    ])
    def test_get_mask_card_number_invalid(self, invalid_card: int) -> None:
        """Тест маскировки невалидного номера карты."""
        with pytest.raises(ValueError):
            get_mask_card_number(invalid_card)

    @pytest.mark.parametrize("account_number, expected", [
        (73654108430135874305, "**4305"),
        (64686473678894779589, "**9589"),
        (35383033474447895560, "**5560"),
        (1234, "**1234"),  # минимальная длина
    ])
    def test_get_mask_account_valid(self, account_number: int, expected: str) -> None:
        """Тест маскировки валидного номера счета."""
        result = get_mask_account(account_number)
        assert result == expected

    @pytest.mark.parametrize("invalid_account", [
        123,  # слишком короткий
    ])
    def test_get_mask_account_invalid(self, invalid_account: int) -> None:
        """Тест маскировки невалидного номера счета."""
        with pytest.raises(ValueError):
            get_mask_account(invalid_account)
