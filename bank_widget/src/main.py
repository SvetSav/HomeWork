"""
Главный модуль банковского виджета.
Обеспечивает пользовательский интерфейс и связывает все функциональности.
"""

import logging
import os
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List

# Создаем логгер для модуля main
logger = logging.getLogger('bank_widget.main')
logger.setLevel(logging.DEBUG)

# Убедимся, что у логгера нет обработчиков
if not logger.handlers:
    # Создаем путь к файлу логов
    current_dir = Path(__file__).parent  # src/
    project_root = current_dir.parent    # project_root/
    log_dir = project_root / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'main.log'

    # Настраиваем file_handler
    file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # Настраиваем formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)

    # Добавляем обработчик
    logger.addHandler(file_handler)


def ask_yes_no(question: str) -> bool:
    """
    Задает вопрос с ответом да/нет.

    Args:
        question: Текст вопроса

    Returns:
        True если ответ 'да', False если 'нет'
    """
    while True:
        answer = input(f"{question} (да/нет): ").strip().lower()
        if answer in ('да', 'д', 'yes', 'y'):
            return True
        elif answer in ('нет', 'н', 'no', 'n'):
            return False
        else:
            print("Пожалуйста, ответьте 'да' или 'нет'.")


def get_default_file_path(file_type: str) -> str:
    """
    Возвращает путь к файлу по умолчанию для указанного типа.

    Args:
        file_type: Тип файла ('json', 'csv', 'excel')

    Returns:
        Путь к файлу
    """
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"

    files = {
        'json': data_dir / "transactions.json",
        'csv': data_dir / "transactions.csv",
        'excel': data_dir / "transactions.xlsx"
    }

    file_path = files[file_type]

    # Если файл не существует, создаем тестовые данные
    if not file_path.exists():
        logger.warning(f"Файл {file_path} не найден. Создаем тестовые данные...")
        create_test_files()

    return str(file_path)


def create_test_files() -> None:
    """Создает тестовые файлы если они отсутствуют."""
    try:
        # Пробуем импортировать из внешнего модуля
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from create_test_files import create_test_files as create_files
        create_files()
    except ImportError:
        # Простой способ создания файлов
        import json

        import pandas as pd

        project_root = Path(__file__).parent.parent
        data_dir = project_root / "data"
        data_dir.mkdir(exist_ok=True)

        # Простые тестовые данные
        test_data = [
            {"id": 1, "date": "2024-01-01", "state": "EXECUTED", "amount": 1000, "currency": "RUB"},
            {"id": 2, "date": "2024-01-02", "state": "CANCELED", "amount": 500, "currency": "USD"},
            {"id": 3, "date": "2024-01-03", "state": "EXECUTED", "amount": 1500, "currency": "RUB"},
        ]

        # JSON
        with open(data_dir / "transactions.json", 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)

        # CSV
        df = pd.DataFrame(test_data)
        df.to_csv(data_dir / "transactions.csv", index=False, encoding='utf-8')

        # Excel
        df.to_excel(data_dir / "transactions.xlsx", index=False)

        logger.info("Созданы тестовые файлы в папке data/")


def process_file_type(file_type: str) -> None:
    """
    Обрабатывает файл указанного типа.

    Args:
        file_type: Тип файла ('json', 'csv', 'excel')
    """
    logger.info(f"Обработка файла типа: {file_type}")

    # Получаем путь к файлу по умолчанию
    file_path = get_default_file_path(file_type)

    print(f"\nДля обработки выбран {file_type.upper()}-файл.")
    print(f"Путь к файлу: {file_path}")

    try:
        # Чтение файла
        if file_type == "json":
            from src.utils import load_json_data
            transactions = load_json_data(file_path)
        elif file_type == "csv":
            from src.file_reader import read_csv_file
            transactions = read_csv_file(file_path)
        elif file_type == "excel":
            from src.file_reader import read_excel_file
            transactions = read_excel_file(file_path)
        else:
            print("Неподдерживаемый тип файла")
            return

        if transactions is None:
            print("Не удалось загрузить данные из файла.")
            return

        print(f"\nЗагружено {len(transactions)} транзакций.")

        if not transactions:
            print("Файл не содержит транзакций или пуст.")
            return

        # Получаем доступные статусы из данных
        statuses = get_available_statuses(transactions)

        if statuses:
            print(f"\nДоступные для фильтровки статусы: {', '.join(sorted(statuses))}")
        else:
            print("\nВ данных не найдены статусы транзакций.")
            if transactions:
                print("\nСтруктура данных:")
                first_transaction = transactions[0]
                print(f"Доступные поля: {', '.join(first_transaction.keys())}")

        # Запрос статуса для фильтрации
        while True:
            print("\n" + "-" * 50)
            state_input = input("Введите статус, по которому необходимо выполнить фильтрацию\n"
                                "(или 'назад' для возврата в меню): ").strip()

            if state_input.lower() in ('назад', 'back', 'отмена', 'cancel'):
                print("Возврат в главное меню...")
                return

            if not state_input:
                print("Статус не может быть пустым.")
                continue

            # Проверяем, есть ли такой статус в данных
            if statuses and state_input.upper() not in [s.upper() for s in statuses]:
                print(f"\nСтатус операции '{state_input}' недоступен.")
                if statuses:
                    print(f"Доступные статусы: {', '.join(sorted(statuses))}")
                continue

            break

        # Фильтрация
        from src.processing import filter_by_state
        filtered_transactions = filter_by_state(transactions, state_input)

        if filtered_transactions:
            print(f"\nОперации отфильтрованы по статусу '{state_input.upper()}'")
            print(f"Найдено {len(filtered_transactions)} транзакций.")

            # Предлагаем дополнительные действия
            if ask_yes_no("\nПоказать первые 5 транзакций?"):
                print("\nПервые 5 транзакций:")
                print("-" * 50)
                for i, transaction in enumerate(filtered_transactions[:5], 1):
                    print(f"\nТранзакция {i}:")
                    for key, value in list(transaction.items())[:5]:  # Показываем первые 5 полей
                        print(f"  {key}: {value}")

                    if len(transaction) > 5:
                        print(f"  ... и еще {len(transaction) - 5} полей")

            if ask_yes_no("\nОтсортировать транзакции по дате (новые первыми)?"):
                from src.processing import sort_by_date
                sorted_transactions = sort_by_date(filtered_transactions, reverse=True)
                print("\n✓ Транзакции отсортированы по дате (от новых к старым)")

                if ask_yes_no("Показать 3 самые новые транзакции?"):
                    print("\n3 самые новые транзакции:")
                    print("-" * 50)
                    for i, transaction in enumerate(sorted_transactions[:3], 1):
                        date = transaction.get('date', 'N/A')
                        desc = transaction.get('description', 'N/A')
                        amount = transaction.get('amount', 'N/A')
                        currency = transaction.get('currency', 'N/A')

                        print(f"\n{i}. {date}")
                        print(f"   Описание: {desc[:50]}{'...' if len(desc) > 50 else ''}")
                        print(f"   Сумма: {amount} {currency}")

        else:
            print(f"\nОперации отфильтрованы по статусу '{state_input.upper()}'")
            print("Найдено 0 транзакций.")
            print("Не найдено транзакций с выбранным статусом.")

            if ask_yes_no("Попробовать другой статус?"):
                # Возвращаемся к выбору статуса
                return process_file_type(file_type)

    except FileNotFoundError as e:
        print(f"\nОшибка: Файл не найден: {e}")
        print("Убедитесь, что файл существует в папке data/")
    except Exception as e:
        logger.error(f"Ошибка при обработке файла {file_path}: {e}")
        print(f"\nОшибка при обработке файла: {e}")


def get_available_statuses(transactions: List[Dict[str, Any]]) -> set:
    """
    Получает доступные статусы из транзакций.

    Args:
        transactions: Список транзакций

    Returns:
        Множество уникальных статусов
    """
    statuses = set()
    possible_state_columns = ['state', 'status', 'State', 'Status', 'статус']

    for transaction in transactions:
        for col in possible_state_columns:
            if col in transaction and transaction[col]:
                status = str(transaction[col]).strip()
                if status:
                    statuses.add(status.upper())

    return statuses


def main() -> None:
    """
    Главная функция программы.
    Реализует пользовательский интерфейс и связывает все функциональности.
    """
    logger.info("Запуск банковского виджета")

    print("=" * 60)
    print("Привет! Добро пожаловать в программу работы с банковскими транзакциями.")
    print("=" * 60)

    # Проверяем наличие файлов данных
    print("\nПроверка доступных файлов данных...")
    for file_type, ext in [('JSON', '.json'), ('CSV', '.csv'), ('Excel', '.xlsx')]:
        file_path = get_default_file_path(file_type.lower())
        if os.path.exists(file_path):
            print(f"✓ {file_type} файл: {file_path}")
        else:
            print(f"✗ {file_type} файл не найден: {file_path}")

    while True:
        print("\n" + "=" * 50)
        print("МЕНЮ:")
        print("1. Получить информацию о транзакциях из JSON-файла")
        print("2. Получить информацию о транзакциях из CSV-файла")
        print("3. Получить информацию о транзакциях из XLSX-файла")
        print("4. Выход")
        print("=" * 50)

        choice = input("Ваш выбор (1-4): ").strip()

        if choice == "1":
            process_file_type("json")
        elif choice == "2":
            process_file_type("csv")
        elif choice == "3":
            process_file_type("excel")
        elif choice == "4":
            print("\nВыход из программы. До свидания!")
            logger.info("Завершение работы банковского виджета")
            break
        else:
            print("\nНеверный выбор. Пожалуйста, выберите от 1 до 4.")


if __name__ == "__main__":
    main()
