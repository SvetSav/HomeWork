"""
Главный модуль банковского виджета.
Линейная версия без рекурсии.
"""

import os
from typing import Any
from typing import Dict
from typing import List


def debug_print(message: str) -> None:
    """Печать отладочных сообщений."""
    print(f"[DEBUG] {message}")


def load_transactions(choice: str, base_dir: str) -> List[Dict[str, Any]]:
    """Загружает транзакции из выбранного файла."""
    debug_print(f"Начало load_transactions, выбор: {choice}")

    file_paths = {
        "1": ("JSON", os.path.join(base_dir, "../data/transactions.json")),
        "2": ("CSV", os.path.join(base_dir, "../data/transactions.csv")),
        "3": ("Excel", os.path.join(base_dir, "../data/transactions.xlsx")),
    }

    if choice not in file_paths:
        debug_print(f"Неверный выбор: {choice}")
        return []

    file_type, file_path = file_paths[choice]
    debug_print(f"Загрузка {file_type} файла: {file_path}")

    try:
        if choice == "1":
            from src.utils import load_json_data

            transactions = load_json_data(file_path)
        elif choice == "2":
            from src.file_reader import read_csv_file

            transactions = read_csv_file(file_path)
        elif choice == "3":
            from src.file_reader import read_excel_file

            transactions = read_excel_file(file_path)
        else:
            return []

        debug_print(f"Загружено {len(transactions) if transactions else 0} транзакций")
        return transactions if transactions else []

    except Exception as e:
        debug_print(f"Ошибка загрузки: {e}")
        return []


def filter_by_status_interactive(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Интерактивная фильтрация транзакций по статусу."""
    debug_print("Начало filter_by_status_interactive")

    if not transactions:
        debug_print("Нет транзакций для фильтрации")
        return []

    # Получаем уникальные статусы из данных
    valid_statuses = set()
    for transaction in transactions:
        state = transaction.get("state")
        if state:
            valid_statuses.add(state.upper())

    if not valid_statuses:
        debug_print("Не найдено статусов в данных")
        return transactions

    debug_print(f"Доступные статусы в данных: {valid_statuses}")

    while True:
        print("\n" + "=" * 60)
        print("ФИЛЬТРАЦИЯ ПО СТАТУСУ")
        print(f"Доступные статусы: {', '.join(sorted(valid_statuses))}")
        print("Введите 'назад' для возврата в главное меню")
        print("=" * 60)

        status_input = input("Введите статус: ").strip().upper()
        debug_print(f"Пользователь ввел статус: {status_input}")

        if status_input == "НАЗАД":
            debug_print("Пользователь выбрал 'назад'")
            return []

        if not status_input:
            print("Статус не может быть пустым.")
            continue

        if status_input not in valid_statuses:
            print(f'Статус операции "{status_input}" недоступен.')
            print(f'Доступные статусы: {", ".join(sorted(valid_statuses))}')
            continue

        debug_print(f"Применение фильтра по статусу: {status_input}")
        from src.processing import filter_by_state

        filtered = filter_by_state(transactions, status_input)

        if filtered:
            print(f'\n✓ Операции отфильтрованы по статусу "{status_input}"')
            print(f"✓ Найдено {len(filtered)} транзакций")
            debug_print(f"После фильтрации осталось {len(filtered)} транзакций")
            return filtered
        else:
            print(f'\n✗ Не найдено транзакций со статусом "{status_input}"')
            print("Попробуйте другой статус.")
            # НЕ вызываем рекурсивно! Просто продолжаем цикл


def ask_yes_no_question(question: str) -> bool:
    """Задает вопрос с ответом да/нет."""
    debug_print(f"Задан вопрос: {question}")

    while True:
        answer = input(f"{question} (да/нет): ").strip().lower()
        debug_print(f"Ответ пользователя: {answer}")

        if answer in ["да", "д", "yes", "y"]:
            return True
        elif answer in ["нет", "н", "no", "n"]:
            return False
        else:
            print('Пожалуйста, введите "Да" или "Нет".')


def process_transactions(transactions: List[Dict[str, Any]]) -> None:
    """Обработка загруженных транзакций."""
    debug_print(f"Начало process_transactions с {len(transactions)} транзакциями")

    if not transactions:
        print("Нет транзакций для обработки.")
        return

    current_transactions = transactions.copy()

    # Шаг 1: Фильтрация по статусу
    debug_print("Шаг 1: Фильтрация по статусу")
    filtered = filter_by_status_interactive(current_transactions)

    if not filtered:
        debug_print("Фильтрация отменена или не дала результатов")
        print("\nФильтрация отменена.")
        return

    current_transactions = filtered

    # Шаг 2: Сортировка по дате
    debug_print("Шаг 2: Проверка сортировки")
    if ask_yes_no_question("\nОтсортировать операции по дате?"):
        debug_print("Пользователь выбрал сортировку")

        print("\nОтсортировать по возрастанию или по убыванию?")
        sort_type = input("(по возрастанию/по убыванию): ").strip().lower()
        debug_print(f"Тип сортировки: {sort_type}")

        from src.processing import sort_by_date

        if sort_type == "по возрастанию":
            current_transactions = sort_by_date(current_transactions, reverse=False)
            print("✓ Транзакции отсортированы по возрастанию даты")
        else:
            current_transactions = sort_by_date(current_transactions, reverse=True)
            print("✓ Транзакции отсортированы по убыванию даты")
    else:
        debug_print("Пользователь отказался от сортировки")

    # Шаг 3: Фильтр по валюте
    debug_print("Шаг 3: Проверка фильтра по валюте")
    if ask_yes_no_question("\nВыводить только рублевые транзакции?"):
        debug_print("Применение фильтра по валюте RUB")
        from src.generators import filter_by_currency

        # ИСПРАВЛЕНИЕ: Преобразуем генератор в список
        rub_transactions = list(filter_by_currency(current_transactions, "RUB"))

        if rub_transactions:
            current_transactions = rub_transactions
            print(f"✓ Выводятся только рублевые транзакции ({len(current_transactions)} шт.)")
        else:
            print("✗ Рублевых транзакций не найдено")
            # Можно спросить, продолжить ли с текущими транзакциями
            if ask_yes_no_question("Продолжить с текущими транзакциями?"):
                print("Продолжаем без фильтрации по валюте")
            else:
                print("Операция отменена")
                return

    # Шаг 4: Фильтр по ключевому слову
    debug_print("Шаг 4: Проверка фильтра по ключевому слову")
    if ask_yes_no_question("\nОтфильтровать по слову в описании?"):
        debug_print("Пользователь выбрал фильтр по ключевому слову")

        keyword = input("\nВведите слово для поиска: ").strip()
        debug_print(f"Ключевое слово: {keyword}")

        if keyword:
            from src.processing import process_bank_search

            searched_generator = process_bank_search(current_transactions, keyword)
            current_transactions = list(searched_generator)

            if current_transactions:
                print(f"✓ Найдено {len(current_transactions)} транзакций с '{keyword}'")
            else:
                print(f"✗ Не найдено транзакций с '{keyword}'")
        else:
            debug_print("Ключевое слово не введено")
    else:
        debug_print("Фильтр по ключевому слову отменен")

    # Шаг 5: Вывод результатов
    debug_print("Шаг 5: Вывод результатов")
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ ОБРАБОТКИ")
    print("=" * 60)

    if not current_transactions:
        print("После обработки не осталось транзакций.")
        return

    transactions_list = list(current_transactions)
    print(f"Итоговое количество транзакций: {len(transactions_list)}")

    # Показать результаты
    print("\nПервые 5 транзакций:")
    print("-" * 40)

    for i, transaction in enumerate(current_transactions[:5], 1):
        print(f"\n{i}. {transaction.get('date', 'Н/Д')}")
        print(f"   Описание: {transaction.get('description', 'Н/Д')}")
        print(f"   Статус: {transaction.get('state', 'Н/Д')}")
        print(f"   Сумма: {transaction.get('amount', 'Н/Д')} {transaction.get('currency', '')}")

    if len(current_transactions) > 5:
        print(f"\n... и еще {len(current_transactions) - 5} транзакций.")

    debug_print(f"Завершение process_transactions, обработано {len(current_transactions)} транзакций")


def main() -> None:
    """Главная функция программы."""
    debug_print("=" * 60)
    debug_print("ЗАПУСК ПРОГРАММЫ")
    debug_print("=" * 60)

    print("\n" + "=" * 60)
    print("ПРИЛОЖЕНИЕ ДЛЯ РАБОТЫ С БАНКОВСКИМИ ТРАНЗАКЦИЯМИ")
    print("=" * 60)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    debug_print(f"Базовый каталог: {base_dir}")

    # Главный цикл программы
    while True:
        debug_print("\nНачало главного цикла")

        print("\n" + "=" * 60)
        print("ГЛАВНОЕ МЕНЮ")
        print("Выберите необходимый пункт меню:")
        print("1. Получить информацию о транзакциях из JSON-файла")
        print("2. Получить информацию о транзакциях из CSV-файла")
        print("3. Получить информацию о транзакциях из XLSX-файла")
        print("4. Выход")
        print("=" * 60)

        choice = input("Ваш выбор (1-4): ").strip()
        debug_print(f"Выбор пользователя в главном меню: {choice}")

        if choice == "4":
            debug_print("Пользователь выбрал выход")
            print("\n" + "=" * 60)
            print("ВЫХОД ИЗ ПРОГРАММЫ")
            print("Спасибо за использование!")
            print("=" * 60)
            break

        if choice not in ["1", "2", "3"]:
            print("\n❌ Неверный выбор. Пожалуйста, выберите 1, 2, 3 или 4.")
            continue

        # Загрузка транзакций
        debug_print(f"Загрузка транзакций для выбора {choice}")
        transactions = load_transactions(choice, base_dir)

        if not transactions:
            print("\n❌ Не удалось загрузить транзакции. Файл пуст или не найден.")
            print("Убедитесь, что файлы находятся в папке data/")
            continue

        print(f"\n✓ Загружено {len(transactions)} транзакций")

        # Обработка транзакций
        debug_print("Переход к обработке транзакций")
        process_transactions(transactions)

        debug_print("Возврат в главное меню")

        # Спросить, хочет ли пользователь продолжить
        print("\n" + "=" * 60)
        if not ask_yes_no_question("Хотите обработать другой файл?"):
            debug_print("Пользователь отказался от продолжения")
            print("\n" + "=" * 60)
            print("ВЫХОД ИЗ ПРОГРАММЫ")
            print("Спасибо за использование!")
            print("=" * 60)
            break
        else:
            debug_print("Пользователь выбрал продолжение")

    debug_print("=" * 60)
    debug_print("ЗАВЕРШЕНИЕ ПРОГРАММЫ")
    debug_print("=" * 60)


if __name__ == "__main__":
    DEBUG_MODE = False
    main()
