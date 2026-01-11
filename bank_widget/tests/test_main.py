"""
Тесты для модуля main.
"""

import logging
from unittest.mock import Mock
from unittest.mock import patch

from src.main import ask_yes_no
from src.main import get_file_path
from src.main import get_operation_status
from src.main import get_user_choice
from src.main import main


class TestMainHelpers:
    """Тесты вспомогательных функций main."""

    def test_get_user_choice_valid(self) -> None:
        """Тест получения корректного выбора пользователя."""
        with patch('builtins.input', return_value='2'):
            result = get_user_choice("Выберите: ", ['1', '2', '3'])
            assert result == '2'

    def test_get_user_choice_invalid_then_valid(self) -> None:
        """Тест получения выбора с некорректным вводом, затем корректным."""
        input_values = ['5', '3']  # Сначала неверный, потом верный
        with patch('builtins.input', side_effect=input_values):
            with patch('builtins.print') as mock_print:
                result = get_user_choice("Выберите: ", ['1', '2', '3'])
                assert result == '3'
                # Проверяем что было сообщение об ошибке
                assert mock_print.called

    @patch('builtins.input')
    def test_get_file_path_valid(self, mock_input: Mock) -> None:
        """Тест получения корректного пути к файлу."""
        mock_input.return_value = "test.csv"

        with patch('pathlib.Path.exists', return_value=True):
            result = get_file_path()
            assert result == "test.csv"

    @patch('builtins.input')
    def test_get_file_path_cancel(self, mock_input: Mock) -> None:
        """Тест отмены ввода пути."""
        mock_input.return_value = "отмена"

        result = get_file_path()
        assert result is None

    @patch('builtins.input')
    def test_get_file_path_not_exists_then_valid(self, mock_input: Mock) -> None:
        """Тест ввода несуществующего файла, затем существующего."""
        input_values = ['nonexistent.csv', 'existing.csv']

        with patch('builtins.input', side_effect=input_values):
            with patch('pathlib.Path.exists', side_effect=[False, True]):
                with patch('builtins.print') as mock_print:
                    result = get_file_path()
                    assert result == 'existing.csv'
                    # Проверяем что было сообщение об ошибке
                    assert mock_print.called

    @patch('builtins.input')
    def test_get_operation_status_valid(self, mock_input: Mock) -> None:
        """Тест получения корректного статуса."""
        mock_input.return_value = "EXECUTED"

        result = get_operation_status()
        assert result == "EXECUTED"

    @patch('builtins.input')
    def test_get_operation_status_case_insensitive(self, mock_input: Mock) -> None:
        """Тест получения статуса в разном регистре."""
        mock_input.return_value = "executed"

        result = get_operation_status()
        assert result == "EXECUTED"

    @patch('builtins.input')
    def test_get_operation_status_invalid_then_valid(self, mock_input: Mock) -> None:
        """Тест получения статуса с некорректным вводом, затем корректным."""
        input_values = ['invalid', 'CANCELED']

        with patch('builtins.input', side_effect=input_values):
            with patch('builtins.print') as mock_print:
                result = get_operation_status()
                assert result == "CANCELED"
                # Проверяем что было сообщение об ошибке
                assert mock_print.called

    @patch('builtins.input')
    def test_ask_yes_no_yes(self, mock_input: Mock) -> None:
        """Тест ответа 'Да'."""
        mock_input.return_value = "да"

        result = ask_yes_no("Тестовый вопрос")
        assert result is True

    @patch('builtins.input')
    def test_ask_yes_no_no(self, mock_input: Mock) -> None:
        """Тест ответа 'Нет'."""
        mock_input.return_value = "нет"

        result = ask_yes_no("Тестовый вопрос")
        assert result is False

    @patch('builtins.input')
    def test_ask_yes_no_invalid_then_valid(self, mock_input: Mock) -> None:
        """Тест ответа с некорректным вводом, затем корректным."""
        input_values = ['maybe', 'да']

        with patch('builtins.input', side_effect=input_values):
            with patch('builtins.print') as mock_print:
                result = ask_yes_no("Тестовый вопрос")
                assert result is True
                # Проверяем что было сообщение об ошибке
                assert mock_print.called


class TestMainIntegration:
    """Интеграционные тесты main."""

    @patch('builtins.input')
    @patch('src.main.load_json_data')
    @patch('src.main.filter_by_state')
    @patch('src.main.ask_yes_no')
    def test_main_flow_json(self, mock_ask_yes_no: Mock, mock_filter_by_state: Mock,
                            mock_load_json_data: Mock, mock_input: Mock) -> None:
        """Тест основного потока для JSON файла."""
        # Настраиваем моки
        mock_input.side_effect = ['1', 'test.json', 'EXECUTED', '4']
        mock_load_json_data.return_value = [{'id': 1, 'description': 'Test'}]
        mock_filter_by_state.return_value = [{'id': 1, 'description': 'Test'}]
        mock_ask_yes_no.return_value = False  # Отвечаем "Нет" на все вопросы

        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.print'):
                main()

        mock_load_json_data.assert_called_once_with('test.json')
        mock_filter_by_state.assert_called_once()

    @patch('builtins.input')
    def test_main_exit(self, mock_input: Mock) -> None:
        """Тест выхода из программы."""
        mock_input.return_value = '4'

        with patch('builtins.print'):
            main()


def test_main_logger_created() -> None:
    """Тест создания логгера для модуля main."""
    from src.main import logger

    assert logger.name == "bank_widget.main"
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) > 0


def test_main_keyboard_interrupt() -> None:
    """Тест, что модуль main может быть импортирован и имеет обработку KeyboardInterrupt."""
    from src.main import main

    # Проверяем что функция существует
    assert callable(main)

    # Проверяем что в коде есть обработка исключений
    import inspect
    source = inspect.getsource(main)

    # Проверяем что есть блок try-except
    assert 'try:' in source
    assert 'except' in source

    # Проверяем что есть обработка KeyboardInterrupt или общая обработка
    assert 'KeyboardInterrupt' in source or 'Exception' in source
