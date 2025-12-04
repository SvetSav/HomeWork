"""Основной модуль для демонстрации функциональности маскировки."""

from src.masks import get_mask_account, get_mask_card_number


def main() -> None:
    """Демонстрация функции маскировки."""
    # Маскировка номера тестовой карточки
    card_number = 7000792289606361
    masked_card = get_mask_card_number(card_number)
    print(f"Card: {card_number} -> {masked_card}")

    # Маскировка номера тестового счета
    account_number = 73654108430135874305
    masked_account = get_mask_account(account_number)
    print(f"Account: {account_number} -> {masked_account}")


if __name__ == "__main__":
    main()