"""
Тесты для главного модуля приложения.
"""

import sys
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from unittest.mock import Mock
from unittest.mock import patch

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from main import ask_yes_no  # noqa: E402
from main import get_available_statuses  # noqa: E402
from main import get_default_file_path  # noqa: E402
from main import main  # noqa: E402
from main import process_file_type  # noqa: E402


class TestMainFunctions:
    """Тесты основных функций главного модуля."""

    def test_get_default_file_path_json(self) -> None:
        """Тест получения пути к JSON файлу."""
        path = get_default_file_path("json")
        assert isinstance(path, str)
        assert path.endswith(".json")

    def test_get_default_file_path_csv(self) -> None:
        """Тест получения пути к CSV файлу."""
        path = get_default_file_path("csv")
        assert isinstance(path, str)
        assert path.endswith(".csv")

    def test_get_default_file_path_excel(self) -> None:
        """Тест получения пути к Excel файлу."""
        path = get_default_file_path("excel")
        assert isinstance(path, str)
        assert path.endswith(".xlsx")

    def test_ask_yes_no_yes(self) -> None:
        """Тест функции ask_yes_no с положительным ответом."""
        with patch('builtins.input', return_value='да'):
            result = ask_yes_no("Тестовый вопрос")
            assert result is True

    def test_ask_yes_no_no(self) -> None:
        """Тест функции ask_yes_no с отрицательным ответом."""
        with patch('builtins.input', return_value='нет'):
            result = ask_yes_no("Тестовый вопрос")
            assert result is False

    def test_ask_yes_no_retry(self) -> None:
        """Тест функции ask_yes_no с повторным вводом."""
        with patch('builtins.input', side_effect=['неверно', 'да']):
            result = ask_yes_no("Тестовый вопрос")
            assert result is True

    def test_get_available_statuses(self) -> None:
        """Тест получения доступных статусов."""
        transactions = [
            {'state': 'EXECUTED'},
            {'state': 'CANCELED'},
            {'status': 'PENDING'},
            {'State': 'EXECUTED'},
            {'description': 'Test'},  # Без статуса
        ]

        statuses = get_available_statuses(transactions)

        assert isinstance(statuses, set)
        assert 'EXECUTED' in statuses
        assert 'CANCELED' in statuses
        assert 'PENDING' in statuses

    def test_get_available_statuses_empty(self) -> None:
        """Тест получения статусов из пустого списка."""
        transactions: List[Dict[str, Any]] = []
        statuses = get_available_statuses(transactions)
        assert statuses == set()

    def test_get_available_statuses_no_status_field(self) -> None:
        """Тест получения статусов при отсутствии поля статуса."""
        transactions = [
            {'id': 1, 'description': 'Test'},
            {'id': 2, 'description': 'Test 2'},
        ]
        statuses = get_available_statuses(transactions)
        assert statuses == set()


class TestMainIntegration:
    """Интеграционные тесты главного модуля."""

    @patch('builtins.input')
    @patch('src.utils.load_json_data')  # ПРАВИЛЬНЫЙ ПУТЬ
    @patch('src.processing.filter_by_state')  # ПРАВИЛЬНЫЙ ПУТЬ
    @patch('main.ask_yes_no')  # Или 'src.main.ask_yes_no' если функция в main
    def test_main_flow_json(self, mock_ask_yes_no: Mock, mock_filter_by_state: Mock,
                            mock_load_json_data: Mock, mock_input: Mock) -> None:
        """Тест основного потока для JSON файла."""
        # Настраиваем моки
        mock_input.side_effect = ['1', 'EXECUTED', 'нет', 'нет', '4']
        mock_load_json_data.return_value = [{'id': 1, 'description': 'Test', 'state': 'EXECUTED'}]
        mock_filter_by_state.return_value = [{'id': 1, 'description': 'Test', 'state': 'EXECUTED'}]
        mock_ask_yes_no.return_value = False  # Отвечаем "Нет" на все вопросы

        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.print'):
                main()

    @patch('builtins.input')
    @patch('src.file_reader.read_csv_file')  # ПРАВИЛЬНЫЙ ПУТЬ
    @patch('src.processing.filter_by_state')  # ПРАВИЛЬНЫЙ ПУТЬ
    @patch('main.ask_yes_no')  # Или 'src.main.ask_yes_no'
    def test_main_flow_csv(self, mock_ask_yes_no: Mock, mock_filter_by_state: Mock,
                           mock_read_csv_file: Mock, mock_input: Mock) -> None:
        """Тест основного потока для CSV файла."""
        mock_input.side_effect = ['2', 'EXECUTED', 'нет', 'нет', '4']
        mock_read_csv_file.return_value = [{'id': 1, 'description': 'Test', 'state': 'EXECUTED'}]
        mock_filter_by_state.return_value = [{'id': 1, 'description': 'Test', 'state': 'EXECUTED'}]
        mock_ask_yes_no.return_value = False

        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.print'):
                main()

    @patch('builtins.input')
    @patch('src.file_reader.read_excel_file')  # ПРАВИЛЬНЫЙ ПУТЬ
    @patch('src.processing.filter_by_state')  # ПРАВИЛЬНЫЙ ПУТЬ
    @patch('main.ask_yes_no')  # Или 'src.main.ask_yes_no'
    def test_main_flow_excel(self, mock_ask_yes_no: Mock, mock_filter_by_state: Mock,
                             mock_read_excel_file: Mock, mock_input: Mock) -> None:
        """Тест основного потока для Excel файла."""
        mock_input.side_effect = ['3', 'EXECUTED', 'нет', 'нет', '4']
        mock_read_excel_file.return_value = [{'id': 1, 'description': 'Test', 'state': 'EXECUTED'}]
        mock_filter_by_state.return_value = [{'id': 1, 'description': 'Test', 'state': 'EXECUTED'}]
        mock_ask_yes_no.return_value = False

        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.print'):
                main()

    def test_main_invalid_choice(self) -> None:
        """Тест обработки неверного выбора в меню."""
        with patch('builtins.input', side_effect=['5', '4']):
            with patch('builtins.print') as mock_print:
                main()
                # Проверяем что выводилось сообщение об ошибке
                assert any(
                    'неверный' in str(call).lower()
                    or 'ошибка' in str(call).lower()
                    or 'выберите' in str(call).lower()
                    for call in mock_print.call_args_list
                )

    @patch('builtins.input', return_value='4')
    def test_main_exit(self, mock_input: Mock) -> None:
        """Тест выхода из программы."""
        with patch('builtins.print'):
            main()


def test_process_file_type_json() -> None:
    """Тест обработки JSON файла."""
    with patch('src.utils.load_json_data') as mock_load:
        mock_load.return_value = [{'id': 1, 'state': 'EXECUTED'}]

        with patch('src.processing.filter_by_state') as mock_filter:
            mock_filter.return_value = [{'id': 1, 'state': 'EXECUTED'}]

            with patch('main.ask_yes_no', return_value=False):
                with patch('builtins.input', side_effect=['EXECUTED']):
                    with patch('builtins.print'):
                        process_file_type("json")


def test_process_file_type_csv() -> None:
    """Тест обработки CSV файла."""
    with patch('src.file_reader.read_csv_file') as mock_read:
        mock_read.return_value = [{'id': 1, 'state': 'EXECUTED'}]

        with patch('src.processing.filter_by_state') as mock_filter:
            mock_filter.return_value = [{'id': 1, 'state': 'EXECUTED'}]

            with patch('main.ask_yes_no', return_value=False):
                with patch('builtins.input', side_effect=['EXECUTED']):
                    with patch('builtins.print'):
                        process_file_type("csv")


def test_process_file_type_excel() -> None:
    """Тест обработки Excel файла."""
    with patch('src.file_reader.read_excel_file') as mock_read:
        mock_read.return_value = [{'id': 1, 'state': 'EXECUTED'}]

        with patch('src.processing.filter_by_state') as mock_filter:
            mock_filter.return_value = [{'id': 1, 'state': 'EXECUTED'}]

            with patch('main.ask_yes_no', return_value=False):
                with patch('builtins.input', side_effect=['EXECUTED']):
                    with patch('builtins.print'):
                        process_file_type("excel")


def test_process_file_type_back() -> None:
    """Тест возврата в меню при обработке файла."""
    with patch('src.utils.load_json_data') as mock_load:
        mock_load.return_value = [{'id': 1, 'state': 'EXECUTED'}]

        with patch('builtins.input', side_effect=['назад']):
            with patch('builtins.print'):
                process_file_type("json")


def test_process_file_type_file_not_found() -> None:
    """Тест обработки отсутствующего файла."""
    with patch('pathlib.Path.exists', return_value=False):
        with patch('main.create_test_files') as mock_create:
            with patch('src.utils.load_json_data') as mock_load:
                mock_load.return_value = []

                with patch('builtins.input', side_effect=['EXECUTED']):
                    with patch('builtins.print'):
                        process_file_type("json")
                        mock_create.assert_called_once()
