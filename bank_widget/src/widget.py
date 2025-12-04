def mask_account_card(data: str) -> str:
    """Маскирует номера карт и счетов."""
    # Разделяем строку на название и номер
    parts = data.rsplit(' ', 1)
    if len(parts) != 2:
        return data

    name, number = parts[0], parts[1]

    # Проверяем, является ли это счетом
    if name.lower() == "счет":
        return f"{name} **{number[-4:]}"
    else:
        # Маскировка для карты (формат XXXX XX** **** XXXX)
        masked_number = f"{number[:4]} {number[4:6]}** **** {number[-4:]}"
        return f"{name} {masked_number}"

def mask_card_number(card_number: str) -> str:
    """Маскирует номер карты"""
    return f"{card_number[:4]} {card_number[4:6]}** **** {card_number[-4:]}"


def mask_account_number(account_number: str) -> str:
    """Маскирует номер счета"""
    return f"**{account_number[-4:]}"


# Примеры использования функций
if __name__ == "__main__":
    # Примеры входных данных для проверки функции
    test_cases = [
        "Visa Platinum 7000792289606361",
        "Maestro 7000792289606361",
        "Счет 73654108430135874305",
        "Maestro 1596837868705199",
        "Счет 64686473678894779589",
        "MasterCard 7158300734726758",
        "Счет 35383033474447895560",
        "Visa Classic 6831982476737658",
        "Visa Platinum 8990922113665229",
        "Visa Gold 5999414228426353",
        "Счет 73654108430135874305"
    ]

    print("Тестирование mask_account_card:")
    print("-" * 50)
    for test in test_cases:
        result = mask_account_card(test)
        print(f"Вход:  {test}")
        print(f"Выход: {result}")
        print()

    print("\n" + "=" * 50 + "\n")