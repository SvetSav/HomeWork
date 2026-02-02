"""
Главный модуль банковского виджета.
Линейная версия без рекурсии.
"""

import importlib.util
import os
import sys
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List

import pandas as pd

# Добавляем src в путь поиска модулей
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Импортируем все необходимые функции
try:
    from utils import load_json_data
except ImportError:
    # Альтернативный импорт, если стандартный не работает
    utils_path = os.path.join(os.path.dirname(__file__), 'src', 'utils.py')
    if os.path.exists(utils_path):
        spec = importlib.util.spec_from_file_location("utils", utils_path)
        if spec is not None and spec.loader is not None:
            utils = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(utils)
            load_json_data = utils.load_json_data
        else:
            load_json_data = None
            print("Внимание: не удалось создать спецификацию модуля utils или loader отсутствует")
    else:
        load_json_data = None
        print("Внимание: модуль utils не найден")
try:
    from file_reader import read_csv_file
    from file_reader import read_excel_file
except ImportError:
    read_csv_file = None
    read_excel_file = None

try:
    from processing import filter_by_state
    from processing import process_bank_operations
    from processing import process_bank_search
    from processing import sort_by_date
except ImportError:
    filter_by_state = None
    sort_by_date = None
    process_bank_search = None
    process_bank_operations = None

try:
    from masks import mask_account_number
    from masks import mask_card_number
except ImportError:
    mask_account_number = None
    mask_card_number = None

try:
    from generators import filter_by_currency
except ImportError:
    filter_by_currency = None


def debug_print(message: str) -> None:
    """Печать отладочных сообщений."""
    print(f"[DEBUG] {message}")


def load_transactions(choice: str, base_dir: str) -> List[Dict[str, Any]]:
    """Загружает транзакции из выбранного файла."""
    debug_print(f"Начало load_transactions, выбор: {choice}")

    # ИСПРАВЛЕННЫЙ ПУТЬ К ФАЙЛАМ
    file_paths = {
        "1": ("JSON", os.path.join(base_dir, "../data/operations.json")),
        "2": ("CSV", os.path.join(base_dir, "../data/transactions.csv")),
        "3": ("Excel", os.path.join(base_dir, "../data/transactions_excel.xlsx")),
    }

    if choice not in file_paths:
        debug_print(f"Неверный выбор: {choice}")
        return []

    file_type, file_path = file_paths[choice]
    debug_print(f"Загрузка {file_type} файла: {file_path}")

    if not os.path.exists(file_path):
        print(f"\n❌ Файл {file_type} не найден по пути:")
        print(f"   {file_path}")
        print("\nУбедитесь, что файл существует или выберите другой формат.")
        return []
    else:
        debug_print(f"✅ Файл существует: {file_path}")
        debug_print(f"Размер файла: {os.path.getsize(file_path)} байт")

    try:
        if choice == "1":
            if load_json_data is None:
                raise ImportError("Функция load_json_data не доступна")
            transactions = load_json_data(file_path)
        elif choice == "2":
            if read_csv_file is None:
                raise ImportError("Функция read_csv_file не доступна")
            transactions = read_csv_file(file_path)
        elif choice == "3":
            if read_excel_file is None:
                raise ImportError("Функция read_excel_file не доступна")
            transactions = read_excel_file(file_path)
        else:
            return []

        debug_print(f"Загружено {len(transactions) if transactions else 0} транзакций")
        return transactions if transactions else []

    except FileNotFoundError:
        debug_print(f"Файл не найден: {file_path}")
        # В реальной программе можно вывести сообщение
        if __name__ == "__main__":
            print(f"\n⚠ Файл {file_type} не найден по пути: {file_path}")
        return []
    except Exception as e:
        debug_print(f"Ошибка загрузки: {e}")
        return []


def filter_by_status_interactive(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Интерактивная фильтрация транзакций по статусу."""
    debug_print("Начало filter_by_status_interactive")

    if not transactions:
        debug_print("Нет транзакций для фильтрации")
        return []

    # Получаем уникальные статусы из данных с обработкой разных типов данных
    valid_statuses = set()
    for transaction in transactions:
        state = transaction.get("state")

        # Проверяем и обрабатываем разные типы данных
        if state is not None:
            if isinstance(state, str):
                # Для строк: убираем пробелы и переводим в верхний регистр
                state_clean = state.strip()
                if state_clean:
                    valid_statuses.add(state_clean.upper())
            elif isinstance(state, (int, float)):
                # Для чисел: проверяем не является ли NaN (float('nan') != float('nan'))
                if isinstance(state, float) and state != state:
                    # Это NaN, пропускаем
                    continue
                # Преобразуем число в строку
                try:
                    state_str = str(state).strip()
                    if state_str:
                        valid_statuses.add(state_str.upper())
                except (ValueError, TypeError, AttributeError):
                    pass
            else:
                # Для других типов (например, bool, dict и т.д.)
                try:
                    state_str = str(state).strip()
                    if state_str:
                        valid_statuses.add(state_str.upper())
                except (ValueError, TypeError, AttributeError):
                    pass

    if not valid_statuses:
        debug_print("Не найдено статусов в данных")
        print("⚠ В данных нет валидных статусов транзакций.")
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

        # Проверяем, есть ли такой статус в данных
        found_status = None
        for status in valid_statuses:
            if status_input == status:
                found_status = status
                break

        if not found_status:
            print(f'Статус операции "{status_input}" недоступен.')
            print(f'Доступные статусы: {", ".join(sorted(valid_statuses))}')
            continue

        debug_print(f"Применение фильтра по статусу: {found_status}")

        if filter_by_state is None:
            print("Ошибка: функция filter_by_state не доступна")
            return []

        # Фильтруем транзакции с учетом разных типов данных в поле state
        filtered = []
        for transaction in transactions:
            state = transaction.get("state")

            if state is not None:
                # Приводим state к строке для сравнения
                state_str = ""
                if isinstance(state, str):
                    state_str = state.strip().upper()
                elif isinstance(state, (int, float)):
                    if isinstance(state, float) and state != state:
                        # NaN, пропускаем
                        continue
                    state_str = str(state).strip().upper()
                else:
                    try:
                        state_str = str(state).strip().upper()
                    except (ValueError, TypeError, AttributeError):
                        continue

                if state_str == found_status:
                    filtered.append(transaction)

        if filtered:
            print(f'\n✓ Операции отфильтрованы по статусу "{found_status}"')
            print(f"✓ Найдено {len(filtered)} транзакций")
            debug_print(f"После фильтрации осталось {len(filtered)} транзакций")
            return filtered
        else:
            print(f'\n✗ Не найдено транзакций со статусом "{found_status}"')
            print("Попробуйте другой статус.")
            # Продолжаем цикл для нового ввода


def format_transaction_output(transaction: Dict[str, Any]) -> str:
    """Форматирует вывод транзакции согласно ТЗ."""
    debug_print(f"Форматирование транзакции {transaction.get('id', 'unknown')}")

    try:
        # Форматирование даты
        date_str = "Н/Д"
        if "date" in transaction and transaction["date"]:
            try:
                date_str_raw = str(transaction["date"])
                if "T" in date_str_raw:
                    date_obj = datetime.fromisoformat(date_str_raw.replace("Z", "+00:00"))
                    date_str = date_obj.strftime("%d.%m.%Y")
                else:
                    # Пробуем другие форматы
                    for fmt in ["%Y-%m-%d", "%d.%m.%Y", "%Y-%m-%d %H:%M:%S"]:
                        try:
                            date_obj = datetime.strptime(date_str_raw, fmt)
                            date_str = date_obj.strftime("%d.%m.%Y")
                            break
                        except ValueError:
                            continue
            except (ValueError, TypeError) as e:
                debug_print(f"Ошибка форматирования даты: {e}")
                date_str = "Н/Д"

        # Описание
        description = str(transaction.get("description", "Н/Д"))

        # Маскирование номеров карт/счетов
        from_field = transaction.get("from", "")
        to_field = transaction.get("to", "")

        from_masked = ""
        to_masked = ""

        if from_field:
            from_field_str = str(from_field)
            if "Счет" in from_field_str:
                # Извлекаем последние 4 цифры
                parts = from_field_str.split()
                if len(parts) >= 2:
                    number = parts[-1]
                    from_masked = f"Счет **{number[-4:] if len(number) >= 4 else number}"
                else:
                    from_masked = from_field_str
            else:
                # Маскирование карты: XXXX XX** **** XXXX
                parts = from_field_str.rsplit(' ', 1)
                if len(parts) == 2:
                    name, number = parts
                    number_clean = number.replace(" ", "")
                    if len(number_clean) == 16 and number_clean.isdigit():
                        from_masked = f"{name} {number_clean[:4]} {number_clean[4:6]}** **** {number_clean[-4:]}"
                    else:
                        from_masked = from_field_str
                else:
                    from_masked = from_field_str

        if to_field:
            to_field_str = str(to_field)
            if "Счет" in to_field_str:
                parts = to_field_str.split()
                if len(parts) >= 2:
                    number = parts[-1]
                    to_masked = f"Счет **{number[-4:] if len(number) >= 4 else number}"
                else:
                    to_masked = to_field_str
            else:
                parts = to_field_str.rsplit(' ', 1)
                if len(parts) == 2:
                    name, number = parts
                    number_clean = number.replace(" ", "")
                    if len(number_clean) == 16 and number_clean.isdigit():
                        to_masked = f"{name} {number_clean[:4]} {number_clean[4:6]}** **** {number_clean[-4:]}"
                    else:
                        to_masked = to_field_str
                else:
                    to_masked = to_field_str

        # Сумма - обрабатываем разные типы данных
        amount_raw = transaction.get("amount", "Н/Д")
        currency = transaction.get("currency", "")

        amount_value = "Н/Д"

        # Проверяем тип amount
        if isinstance(amount_raw, dict):
            # Вложенная структура: {"amount": "100", "currency": {"code": "RUB"}}
            amount_value = amount_raw.get("amount", "Н/Д")
            currency_obj = amount_raw.get("currency", {})
            if isinstance(currency_obj, dict):
                currency = currency_obj.get("name", currency_obj.get("code", currency))
        elif amount_raw is None:
            amount_value = "Н/Д"
        else:
            # Простое значение: строка, число и т.д.
            amount_value = str(amount_raw)

        # ОБРАБОТКА ВАЛЮТЫ - КОРРЕКТНОЕ ПРЕОБРАЗОВАНИЕ
        currency_str = ""
        if 'currency' in transaction:
            currency = transaction['currency']

            if isinstance(currency, str):
                currency_str = currency.strip()
                # Убираем точку в конце валюты
                if currency_str.endswith('.'):
                    currency_str = currency_str.rstrip('.')
            elif isinstance(currency, (int, float)):
                # Числовая валюта (например, код валюты как число)
                if isinstance(currency, float) and pd.isna(currency):
                    # Это NaN, используем RUB по умолчанию
                    currency_str = "RUB"  # type: ignore[unreachable]
                else:
                    currency_str = str(currency).strip()
            elif currency is None:
                # None, используем RUB по умолчанию
                currency_str = "RUB"
            else:
                # Другие типы
                try:
                    currency_str = str(currency).strip()
                except (ValueError, TypeError, AttributeError):
                    currency_str = "RUB"
        else:
            # Поле currency отсутствует, используем RUB по умолчанию
            currency_str = "RUB"

        # Форматируем сумму
        if amount_value != "Н/Д" and amount_value:
            # Убираем лишние нули после точки для целых чисел
            try:
                amount_num = float(amount_value)
                if amount_num.is_integer():
                    amount_value = str(int(amount_num))
            except (ValueError, TypeError):
                pass

            # Проверяем, не содержит ли уже amount_value валюту
            if currency_str and currency_str not in amount_value:
                amount_str = f"{amount_value} {currency_str}"
            else:
                amount_str = amount_value
        else:
            amount_str = "Н/Д"

        # Формируем вывод
        result_lines = []
        result_lines.append(f"{date_str} {description}")

        if from_masked and to_masked:
            result_lines.append(f"{from_masked} -> {to_masked}")
        elif to_masked:
            result_lines.append(f"{to_masked}")
        elif from_masked:
            result_lines.append(f"{from_masked}")

        if amount_str:
            # Убедимся, что сумма имеет правильный формат
            if "Сумма:" not in amount_str:
                result_lines.append(f"Сумма: {amount_str}")
            else:
                result_lines.append(amount_str)

        return "\n".join(result_lines)

    except Exception as e:
        debug_print(f"Ошибка форматирования: {e}")
        # Возвращаем хотя бы основную информацию
        date_str = str(transaction.get("date", "Н/Д"))[:10] if transaction.get("date") else "Н/Д"
        description = str(transaction.get("description", "Н/Д"))
        return f"{date_str} {description}"


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

        if sort_by_date is None:
            print("Ошибка: функция sort_by_date не доступна")
            return

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

        if filter_by_currency is None:
            print("Ошибка: функция filter_by_currency не доступна")
            return

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
            if process_bank_search is None:
                print("Ошибка: функция process_bank_search не доступна")
                return

            searched_generator = process_bank_search(current_transactions, keyword)
            current_transactions = list(searched_generator)

            if current_transactions:
                print(f"✓ Найдено {len(current_transactions)} транзакций с '{keyword}'")
            else:
                print(f"✗ Не найдено транзакций с '{keyword}'")
                print("Операция отменена")
                return
        else:
            debug_print("Ключевое слово не введено")
    else:
        debug_print("Фильтр по ключевому слову отменен")

    # Шаг 5: Подсчет операций по категориям
    debug_print("Шаг 5: Подсчет операций по категориям")
    if ask_yes_no_question("\nПодсчитать операции по категориям?"):
        debug_print("Пользователь выбрал подсчет по категориям")

        # Получаем уникальные категории из описаний
        categories = []
        for transaction in current_transactions:
            description = transaction.get("description", "")
            if description and description not in categories:
                categories.append(description)

        if categories and process_bank_operations is not None:
            category_counts = process_bank_operations(current_transactions, categories)

            print("\nКоличество операций по категориям:")
            print("-" * 40)
            for category, count in category_counts.items():
                print(f"{category}: {count}")
            print("-" * 40)

    # Шаг 6: Вывод результатов
    debug_print("Шаг 6: Вывод результатов")
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ ОБРАБОТКИ")
    print("=" * 60)

    if not current_transactions:
        print("После обработки не осталось транзакций.")
        return

    print(f"Итоговое количество транзакций: {len(current_transactions)}")

    # Показать результаты
    print("\nПервые 5 транзакций:")
    print("-" * 60)  # Увеличиваем разделитель

    for i, transaction in enumerate(current_transactions[:5], 1):
        formatted = format_transaction_output(transaction)
        # Разделяем транзакции пустой строкой для читаемости
        print(f"\n{i}.")
        print(formatted)
        print()  # Пустая строка между транзакциями

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

        if choice in ["1", "2", "3"]:
            transactions = load_transactions(choice, base_dir)
            if transactions:
                process_transactions(transactions)
            else:
                print("\nНе удалось загрузить транзакции.")
        else:
            print("\nНеверный выбор. Пожалуйста, введите 1, 2, 3 или 4.")


if __name__ == "__main__":
    main()
