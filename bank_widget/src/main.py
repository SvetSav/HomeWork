"""
Главный модуль банковского виджета.
Содержит основную логику взаимодействия с пользователем.
"""

import logging
import sys
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from .file_reader import read_financial_data
from .operations import count_transactions_by_category
from .operations import filter_transactions_by_currency
from .operations import format_transaction_for_display
from .operations import search_transactions_by_description
from .processing import filter_by_state
from .processing import sort_by_date
from .utils import load_json_data

# Создаем логгер для модуля main
logger = logging.getLogger('bank_widget.main')
logger.setLevel(logging.DEBUG)

# Убедимся, что у логгера нет обработчиков
if not logger.handlers:
    # Создаем путь к файлу логов
    current_dir = Path(__file__).parent  # src/
    project_root = current_dir.parent  # project_root/
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
    logger.addHandler(file_handler)


def get_user_choice(prompt: str, valid_choices: List[str]) -> str:
    """
    Получает выбор пользователя с валидацией.

    Args:
        prompt: Текст запроса
        valid_choices: Список допустимых вариантов

    Returns:
        Выбор пользователя
    """
    while True:
        choice = input(prompt).strip()
        if choice in valid_choices:
            return choice
        print(f"Неверный выбор. Допустимые варианты: {', '.join(valid_choices)}")


def get_file_path() -> Optional[str]:
    """
    Запрашивает у пользователя путь к файлу.

    Returns:
        Путь к файлу или None если отменено
    """
    print("\nВведите путь к файлу (или 'отмена' для возврата в меню):")
    file_path = input("> ").strip()

    if file_path.lower() in ['отмена', 'cancel', 'выход', 'exit']:
        return None

    if not Path(file_path).exists():
        print(f"Файл '{file_path}' не найден.")
        return get_file_path()

    return file_path


def get_operation_status() -> str:
    """
    Получает статус операций от пользователя.

    Returns:
        Статус операций
    """
    valid_statuses = ['EXECUTED', 'CANCELED', 'PENDING']

    print("\nДоступные для фильтровки статусы: EXECUTED, CANCELED, PENDING")

    while True:
        status = input("Введите статус, по которому необходимо выполнить фильтрацию: ").strip().upper()

        if status in valid_statuses:
            return status
        else:
            print(f"Статус операции '{status}' недоступен.")
            print("Доступные для фильтровки статусы: EXECUTED, CANCELED, PENDING")


def ask_yes_no(question: str) -> bool:
    """
    Задает вопрос с ответом Да/Нет.

    Args:
        question: Вопрос

    Returns:
        True если Да, False если Нет
    """
    while True:
        answer = input(f"{question} (Да/Нет): ").strip().lower()

        if answer in ['да', 'д', 'yes', 'y']:
            return True
        elif answer in ['нет', 'н', 'no', 'n']:
            return False
        else:
            print("Пожалуйста, ответьте 'Да' или 'Нет'")


def main() -> None:
    """
    Главная функция программы.
    Реализует пользовательский интерфейс и связывает все функциональности.
    """
    logger.info("Запуск банковского виджета")

    print("=" * 60)
    print("Привет! Добро пожаловать в программу работы с банковскими транзакциями.")
    print("Выберите необходимый пункт меню:")
    print("=" * 60)

    transactions: List[Dict[str, Any]] = []

    while True:
        print("\nМЕНЮ:")
        print("1. Получить информацию о транзакциях из JSON-файла")
        print("2. Получить информацию о транзакциях из CSV-файла")
        print("3. Получить информацию о транзакциях из XLSX-файла")
        print("4. Выход")

        choice = get_user_choice("\nВаш выбор (1-4): ", ['1', '2', '3', '4'])

        if choice == '4':
            print("\nСпасибо за использование программы! До свидания!")
            logger.info("Завершение работы программы")
            break

        # Определяем тип файла
        file_types = {'1': 'JSON', '2': 'CSV', '3': 'XLSX'}
        file_type = file_types[choice]

        print(f"\nДля обработки выбран {file_type}-файл.")

        # Получаем путь к файлу
        file_path = get_file_path()
        if file_path is None:
            continue

        try:
            # Загружаем данные
            if choice == '1':
                transactions = load_json_data(file_path)
            else:
                transactions = read_financial_data(file_path)

            if not transactions:
                print(f"\nФайл '{file_path}' пуст или не содержит транзакций.")
                continue

            print(f"\nЗагружено {len(transactions)} транзакций.")

            # Фильтрация по статусу
            status = get_operation_status()
            filtered_transactions = filter_by_state(transactions, status)
            print(f"\nОперации отфильтрованы по статусу '{status}'")
            print(f"Найдено {len(filtered_transactions)} транзакций.")

            if not filtered_transactions:
                print("Не найдено транзакций с выбранным статусом.")
                continue

            # Сортировка по дате
            if ask_yes_no("\nОтсортировать операции по дате?"):
                if ask_yes_no("Отсортировать по возрастанию или по убыванию? "
                              "(Да - по возрастанию, Нет - по убыванию)"):
                    filtered_transactions = sort_by_date(filtered_transactions, reverse=False)
                    print("Транзакции отсортированы по возрастанию даты.")
                else:
                    filtered_transactions = sort_by_date(filtered_transactions, reverse=True)
                    print("Транзакции отсортированы по убыванию даты.")

            # Фильтрация по валюте
            if ask_yes_no("\nВыводить только рублевые транзакции?"):
                filtered_transactions = filter_transactions_by_currency(filtered_transactions, "RUB")
                print(f"Оставлено {len(filtered_transactions)} рублевых транзакций.")

            # Поиск по описанию
            if ask_yes_no("\nОтфильтровать список транзакций по определенному слову в описании?"):
                search_word = input("Введите слово для поиска в описании: ").strip()
                if search_word:
                    filtered_transactions = search_transactions_by_description(filtered_transactions, search_word)
                    print(f"Найдено {len(filtered_transactions)} транзакций с словом '{search_word}' в описании.")

            # Вывод результатов
            print("\n" + "=" * 60)
            print("Распечатываю итоговый список транзакций...")
            print("=" * 60)

            if not filtered_transactions:
                print("\nНе найдено ни одной транзакции, подходящей под ваши условия фильтрации")
            else:
                print(f"\nВсего банковских операций в выборке: {len(filtered_transactions)}\n")

                for i, transaction in enumerate(filtered_transactions, 1):
                    print(f"{i}. {format_transaction_for_display(transaction)}")
                    print("-" * 40)

                # Дополнительная статистика
                if ask_yes_no("\nПоказать статистику по категориям транзакций?"):
                    categories_input = input("Введите категории для анализа (через запятую): ").strip()
                    if categories_input:
                        categories = [cat.strip() for cat in categories_input.split(',')]
                        stats = count_transactions_by_category(filtered_transactions, categories)

                        print("\nСтатистика по категориям:")
                        for category, count in stats.items():
                            print(f"  {category}: {count} транзакций")

            logger.info(f"Обработано {len(filtered_transactions)} транзакций")

        except Exception as e:
            print(f"\nОшибка при обработке файла: {e}")
            logger.error(f"Ошибка при обработке файла {file_path}: {e}")
            continue

        # Предложить обработать другой файл
        if not ask_yes_no("\nОбработать другой файл?"):
            print("\nСпасибо за использование программы! До свидания!")
            logger.info("Завершение работы программы")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем.")
        logger.info("Программа прервана пользователем (KeyboardInterrupt)")
    except Exception as e:
        print(f"\nКритическая ошибка: {e}")
        logger.exception("Критическая ошибка в программе")
        sys.exit(1)
