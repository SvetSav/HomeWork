from datetime import datetime


def mask_account_card(data: str) -> str:
    """Маскирует номера карт и счетов."""
    # Разделяем строку на название и номер
    if not data:
        return ""

    # Разделяем строку на название и номер
    parts = data.rsplit(' ', 1)
    if len(parts) != 2:
        return data  # Если нет пробела или формат неверный, возвращаем исходные данные

    name, number = parts[0], parts[1]

    # Проверяем, является ли это счетом
    if name.lower() == "счет":
        return f"{name} **{number[-4:]}"
    # Маскировка для карты (формат XXXX XX** **** XXXX)
    else:
        masked_number = f"{number[:4]} {number[4:6]}** **** {number[-4:]}"
        return f"{name} {masked_number}"


def get_date(date_string: str) -> str:
    """
    Преобразует дату из формата 2024-03-11T02:26:18.671407 в формат ДД.ММ.ГГГГ.

    Аргументы:
        date_string: строка с датой в формате "2024-03-11T02:26:18.671407"

    Возвращает:
        строку с датой в формате "ДД.ММ.ГГГГ"
    """
    try:
        date_object = datetime.fromisoformat(date_string)
        return date_object.strftime("%d.%m.%Y")
    except (ValueError, TypeError):
        # Возвращаем исходную строку в случае ошибки
        return date_string


def mask_card_number(card_number: str) -> str:
    """Маскирует номер карты."""
    return f"{card_number[:4]} {card_number[4:6]}** **** {card_number[-4:]}"


def mask_account_number(account_number: str) -> str:
    """Маскирует номер счета."""
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
        "Счет 73654108430135874305",
    ]

    print("Тестирование mask_account_card:")
    print("-" * 50)
    for test_data in test_cases:
        result = mask_account_card(test_data)
        print(f"Вход:  {test_data}")
        print(f"Выход: {result}")
        print()

    print("\n" + "=" * 50 + "\n")

    # Тестирование функции get_date
    test_dates = [
        "2024-03-11T02:26:18.671407",
        "2023-12-31T23:59:59.999999",
        "2024-01-01T00:00:00.000000",
    ]

    print("Тестирование get_date:")
    print("-" * 50)
    for date_input in test_dates:
        formatted_date = get_date(date_input)
        print(f"Вход:  {date_input}")
        print(f"Выход: {formatted_date}")
        print()
