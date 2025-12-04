"""Модуль для маскировки номеров банковских карт и счетов."""


def get_mask_card_number(card_number: int) -> str:
    """Замаскируйте номер банковской карты по шаблону XXXX XX****** XXXX.
    Аргументы:
    card_number (int): Номер банковской карты в виде целого числа.
    Возвращается:
    str: замаскированный номер карты в формате XXXX XX****** XXXX.
    """
    card_str = str(card_number)
    if len(card_str) != 16:
        raise ValueError("Номер карты должен состоять из 16 цифр.")

    return f"{card_str[:4]} {card_str[4:6]}** **** {card_str[-4:]}"


def get_mask_account(account_number: int) -> str:
    """Замаскируйте номер банковского счета в соответствии с шаблоном **XXXX.
    Аргументы:
    account_number (int): Номер банковского счета в виде целого числа.
    Возвращается:
    str: замаскированный номер счета в формате **XXXX.
    """
    account_str = str(account_number)
    if len(account_str) < 4:
        raise ValueError("Длина номера счета должна составлять не менее 4 цифр.")

    return f"**{account_str[-4:]}"
